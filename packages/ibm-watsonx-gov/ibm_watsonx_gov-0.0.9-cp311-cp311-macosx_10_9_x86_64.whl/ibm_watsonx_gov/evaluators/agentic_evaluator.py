# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os
import time
from pathlib import Path
from threading import Lock
from typing import Annotated, Callable, List, Optional, Set
from uuid import uuid4
from ibm_watsonx_gov.entities.enums import MetricGroup
from pydantic import Field, PrivateAttr
from ibm_watsonx_gov.ai_experiments.ai_experiments_client import \
    AIExperimentsClient
from ibm_watsonx_gov.config import AgenticAIConfiguration
from ibm_watsonx_gov.config.agentic_ai_configuration import \
    TracingConfiguration
from ibm_watsonx_gov.entities import ai_experiment as ai_experiment_entity
from ibm_watsonx_gov.entities.agentic_app import AgenticApp, Node
from ibm_watsonx_gov.entities.ai_evaluation import AIEvaluationAsset
from ibm_watsonx_gov.entities.ai_experiment import (AIExperiment,
                                                    AIExperimentRun,
                                                    AIExperimentRunRequest)
from ibm_watsonx_gov.entities.evaluation_result import (
    AgenticEvaluationResult, AgentMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.evaluators.base_evaluator import BaseEvaluator
from ibm_watsonx_gov.metrics import (AnswerSimilarityMetric,
                                     ContextRelevanceMetric,
                                     FaithfulnessMetric,
                                     ToolCallingHallucinationMetric,
                                     UnsuccessfulRequestsMetric,
                                     AnswerRelevanceMetric, 
                                     PromptSafetyRiskMetric, 
                                     HAPMetric,PIIMetric)
from ibm_watsonx_gov.metrics.answer_similarity.answer_similarity_decorator import \
    AnswerSimilarityDecorator
from ibm_watsonx_gov.metrics.context_relevance.context_relevance_decorator import \
    ContextRelevanceDecorator
from ibm_watsonx_gov.metrics.faithfulness.faithfulness_decorator import \
    FaithfulnessDecorator
from ibm_watsonx_gov.metrics.llm_validation.llm_validation_decorator import \
    LLMValidationDecorator
from ibm_watsonx_gov.metrics.unsuccessful_requests.unsuccesful_requests_decorator import \
    UnsuccessfulRequestsDecorator
from ibm_watsonx_gov.metrics.answer_relevance.answer_relevance_decorator import \
    AnswerRelevanceDecorator
from ibm_watsonx_gov.metric_groups.answer_quality.answer_quality_decorator import \
    AnswerQualityDecorator
from ibm_watsonx_gov.metrics.tool_calling_hallucination.tool_calling_hallucination_decorator import \
    ToolCallingHallucinationDecorator
from ibm_watsonx_gov.metrics.hap.hap_decorator import \
    HAPDecorator
from ibm_watsonx_gov.metrics.pii.pii_decorator import \
    PIIDecorator
from ibm_watsonx_gov.metrics.prompt_safety_risk.prompt_safety_risk_decorator import \
    PromptSafetyRiskDecorator
from ibm_watsonx_gov.metric_groups.content_safety.content_safety_decorator import \
    ContentSafetyDecorator
from ibm_watsonx_gov.traces.span_exporter import WxGovSpanExporter
from ibm_watsonx_gov.traces.span_util import get_attributes
from ibm_watsonx_gov.traces.trace_utils import TraceUtils
from ibm_watsonx_gov.utils.aggregation_util import \
    get_agentic_evaluation_result
from ibm_watsonx_gov.utils.python_utils import add_if_unique
from ibm_watsonx_gov.utils.singleton_meta import SingletonMeta

PROCESS_TRACES = True


try:
    from agent_analytics.instrumentation import agent_analytics_sdk
    from agent_analytics.instrumentation.utils import get_current_trace_id
except ImportError:
    PROCESS_TRACES = False


update_lock = Lock()
TRACE_LOG_FILE_NAME = os.getenv("TRACE_LOG_FILE_NAME", "experiment_traces")
TRACE_LOG_FILE_PATH = os.getenv("TRACE_LOG_FILE_PATH", "./wxgov_traces")


class AgenticEvaluator(BaseEvaluator, metaclass=SingletonMeta):
    """
    The class to evaluate agentic application.

    Examples:
        1. Basic usage with experiment tracking
            .. code-block:: python

                agentic_evaluator = AgenticEvaluator(tracing_configuration=TracingConfiguration(project_id=project_id))
                agentic_evaluator.track_experiment(name="my_experiment")
                agentic_evaluator.start_run(name="run1")
                # Invoke the agentic application
                agentic_evaluator.end_run()
                result = agentic_evaluator.get_result()

        2. Basic usage without experiment tracking
            .. code-block:: python

                agentic_evaluator = AgenticEvaluator()
                agentic_evaluator.start_run()
                # Invoke the agentic application
                agentic_evaluator.end_run()
                result = agentic_evaluator.get_result()
    """
    agentic_app: Annotated[Optional[AgenticApp], Field(
        title="Agentic application configuration details", description="The agentic application configuration details.", default=None)]
    tracing_configuration: Annotated[Optional[TracingConfiguration], Field(
        title="Tracing Configuration", description="The tracing configuration details.", default=None)]
    ai_experiment_client: Annotated[Optional[AIExperimentsClient], Field(
        title="AI experiments client", description="The AI experiment client object.", default=None)]
    __latest_experiment_name: Annotated[Optional[str], PrivateAttr(
        default=None)]
    __latest_experiment_id: Annotated[Optional[str], PrivateAttr(
        default=None)]
    __experiment_results: Annotated[dict,
                                    PrivateAttr(default={})]
    __run_results: Annotated[dict[str, AgenticEvaluationResult],
                             PrivateAttr(default={})]
    __online_metric_results: Annotated[list[AgentMetricResult],
                                       PrivateAttr(default=[])]
    """__metric_results holds the results of all the evaluations done for a particular evaluation instance."""
    __execution_counts: Annotated[dict[str, dict[str, int]],
                                  PrivateAttr(default={})]
    """__execution_counts holds the execution count for a particular node, for a given record_id."""
    __nodes_being_run: Annotated[dict[str, Set[str]],
                                 PrivateAttr(default={})]
    """__nodes_being_run holds the name of the current nodes being run for a given record_id. Multiple decorators can be applied on a single node using chaining. We don't want to hold multiple copies of same node here."""
    __latest_run_name: Annotated[str, PrivateAttr(default=None)]
    __nodes: Annotated[list[Node], PrivateAttr(default=[])]
    __experiment_run_details: Annotated[AIExperimentRun, PrivateAttr(
        default=None)]

    def __init__(self, /, **data):
        """
        Initialize the AgenticEvaluator object and start the tracing framework.
        """
        super().__init__(**data)
        # Initialize the agent analytics sdk
        if PROCESS_TRACES:
            tracing_url = None
            tracing_config = data.get("tracing_configuration")
            if tracing_config:
                tracing_url = tracing_config.tracing_url

            agent_analytics_sdk.initialize_logging(
                tracer_type=agent_analytics_sdk.SUPPORTED_TRACER_TYPES.CUSTOM,
                custom_exporter=WxGovSpanExporter(
                    file_name=TRACE_LOG_FILE_NAME,
                    storage_path=TRACE_LOG_FILE_PATH,
                    service_endpoint=tracing_url
                ),
                new_trace_on_workflow=True,
                resource_attributes={
                    "wxgov.config.agentic_app": self.agentic_app.model_dump_json(exclude_none=True) if self.agentic_app else ""
                }
            )

        self.__latest_experiment_name = "experiment_1"

    def track_experiment(self, name: str = "experiment_1", description: str = None, use_existing: bool = True) -> str:
        """
        Start tracking an experiment for the metrics evaluation. 
        The experiment will be created if it doesn't exist. 
        If an existing experiment with the same name is found, it will be reused based on the flag use_existing. 

        Args:
            project_id (string): The project id to store the experiment.
            name (string): The name of the experiment.
            description (str): The description of the experiment.
            use_existing (bool): The flag to specify if the experiment should be reused if an existing experiment with the given name is found.

        Returns:
            The ID of AI experiment asset
        """
        self.__latest_experiment_name = name
        # Checking if the ai_experiment_name already exists with given name if use_existing is enabled.
        # If it does reuse it, otherwise creating a new ai_experiment
        # Set the experiment_name and experiment_id
        self.ai_experiment_client = AIExperimentsClient(
            api_client=self.api_client,
            project_id=self.tracing_configuration.project_id
        )
        ai_experiment = None
        if use_existing:
            ai_experiment = self.ai_experiment_client.search(name)

        # If no AI experiment exists with specified name or use_existing is False, create new AI experiment
        if not ai_experiment:
            ai_experiment_details = AIExperiment(
                name=name,
                description=description or "AI experiment for Agent governance"
            )
            ai_experiment = self.ai_experiment_client.create(
                ai_experiment_details)

        ai_experiment_id = ai_experiment.asset_id

        # Experiment id will be set when the experiment is tracked and not set when the experiment is not tracked
        self.__latest_experiment_id = ai_experiment_id
        self.__run_results = {}
        return ai_experiment_id

    def start_run(self, run_request: AIExperimentRunRequest = AIExperimentRunRequest(name="run_1")) -> AIExperimentRun:
        """
        Start a run to track the metrics computation within an experiment.
        This method is required to be called before any metrics computation.

        Args:
            run_request (AIExperimentRunRequest): The run_request instance containing name, source_name, source_url

        Returns:
            The details of experiment run like id, name, description etc.
        """
        name = run_request.name
        self.__latest_run_name = name
        self.__experiment_results[self.__latest_experiment_name] = self.__run_results
        self.__start_time = time.time()
        # Having experiment id indicates user is tracking experiments
        if self.__latest_experiment_id:
            # Create run object, having experiment id indicates user is tracking experiments
            self.__experiment_run_details = AIExperimentRun(
                run_id=str(uuid4()),
                run_name=name,
                source_name=run_request.source_name,
                source_url=run_request.source_url
            )

        return self.__experiment_run_details

    def end_run(self):
        """
        End a run to collect and compute the metrics within the current run.
        """
        eval_result = self.__compute_metrics_from_traces()
        self.__run_results[self.__latest_run_name] = eval_result
        # Having experiment id indicates user is tracking experiments and its needed to submit the run details
        if self.__latest_experiment_id:
            self.__store_run_results()

        self.__reset_results()

    def compare_ai_experiments(self,
                               ai_experiments: List[AIExperiment] = None,
                               ai_evaluation_details: AIEvaluationAsset = None
                               ) -> str:
        """
        Creates an AI Evaluation asset to compare AI experiment runs.

        Args:
            ai_experiments (List[AIExperiment], optional):
                List of AI experiments to be compared. If all runs for an experiment need to be compared, then specify the runs value as empty list for the experiment.
            ai_evaluation_details (AIEvaluationAsset, optional):
                An instance of AIEvaluationAsset having details (name, description and metrics configuration)
        Returns:
            An instance of AIEvaluationAsset.

        Examples:
            1. Create AI evaluation with list of experiment IDs
            .. code-block:: python

                # Initialize the API client with credentials
                api_client = APIClient(credentials=Credentials(api_key="", url="wos_url"))

                # Create the instance of Agentic evaluator
                evaluator = AgenticEvaluator(api_client=api_client, tracing_configuration=TracingConfiguration(project_id=project_id))

                # [Optional] Define evaluation configuration
                evaluation_config = EvaluationConfig(
                    monitors={
                        "agentic_ai_quality": {
                            "parameters": {
                                "metrics_configuration": {}
                            }
                        }
                    }
                )

                # Create the evaluation asset
                ai_evaluation_details = AIEvaluationAsset(
                    name="AI Evaluation for agent",
                    evaluation_configuration=evaluation_config
                )

                # Compare two or more AI experiments using the evaluation asset
                ai_experiment1 = AIExperiment(
                    asset_id = ai_experiment_id_1,
                    runs = [<Run1 details>, <Run2 details>] # Run details are returned by the start_run method
                )
                ai_experiment2 = AIExperiment(
                    asset_id = ai_experiment_id_2,
                    runs = [] # Empty list means all runs for this experiment will be compared
                )
                ai_evaluation_asset_href = evaluator.compare_ai_experiments(
                    ai_experiments = [ai_experiment_1, ai_experiment_2],
                    ai_evaluation_details=ai_evaluation_asset
                )
        """
        # If experiment runs to be compared are not provided, using all runs from the latest tracked experiment
        if not ai_experiments:
            ai_experiments = [AIExperiment(
                asset_id=self.__latest_experiment_id, runs=[])]

        # Construct experiment_runs map
        ai_experiment_runs = {exp.asset_id: exp.runs for exp in ai_experiments}

        ai_evaluation_asset = self.ai_experiment_client.create_ai_evaluation_asset(
            ai_experiment_runs=ai_experiment_runs,
            ai_evaluation_details=ai_evaluation_details
        )
        ai_evaluation_asset_href = self.ai_experiment_client.get_ai_evaluation_asset_href(
            ai_evaluation_asset)

        return ai_evaluation_asset_href

    def __compute_metrics_from_traces(self):
        """
        Computes the metrics using the traces collected in the log file.
        """
        if PROCESS_TRACES:
            trace_log_file_path = Path(
                f"{TRACE_LOG_FILE_PATH}/{TRACE_LOG_FILE_NAME}.log")
            spans = []
            for span in TraceUtils.stream_trace_data(trace_log_file_path):
                spans.append(span)

            metrics_result = []
            span_trees = TraceUtils.build_span_trees(spans=spans)
            for span_tree in span_trees:
                # Process only the spans that are associated with the agent application
                attrs = get_attributes(span_tree.span.attributes, [
                                       "traceloop.span.kind"])
                if not attrs.get("traceloop.span.kind") == "workflow":
                    continue

                mr, ns, _ = TraceUtils.compute_metrics_from_trace(span_tree=span_tree,
                                                                  api_client=self.api_client)
                metrics_result.extend(mr)
                for n in ns:
                    add_if_unique(n, self.__nodes, ["name", "func_name"])

            return get_agentic_evaluation_result(
                metrics_result=metrics_result, nodes=self.__nodes)

    def __store_run_results(self):

        aggregated_results = self.get_result().get_aggregated_metrics_results()
        # Fetchig the nodes details to update in experiment run
        nodes = []
        for node in self.get_nodes():
            nodes.append(ai_experiment_entity.Node(
                id=node.func_name, name=node.name))
        self.__experiment_run_details.nodes = nodes
        # Duration of run in seconds
        self.__experiment_run_details.duration = int(
            time.time() - self.__start_time)

        # Storing the run result as attachment and update the run info in AI experiment
        # Todo - keeping the List[AggregateAgentMetricResult] - is that compatible? should store full AgenticEvaluationResult?
        self.ai_experiment_client.update(
            self.__latest_experiment_id,
            self.__experiment_run_details,
            aggregated_results
        )

    def get_nodes(self) -> list[Node]:
        """
        Get the list of nodes used in the agentic application

        Return:
            nodes (list[Node]): The list of nodes used in the agentic application
        """
        return self.__nodes

    def get_result(self, run_name: Optional[str] = None) -> AgenticEvaluationResult:
        """
        Get the AgenticEvaluationResult for the run. By default the result for the latest run is returned.
        Specify the run name to get the result for a specific run.
        Args:
            run_name (string): The evaluation run name
        Return:
            agentic_evaluation_result (AgenticEvaluationResult): The AgenticEvaluationResult object for the run.
        """
        if run_name:
            result = self.__run_results.get(run_name)
        else:
            result = self.__run_results.get(self.__latest_run_name)

        return result

    def get_metric_result(self, metric_name: str, node_name: str) -> AgentMetricResult:
        """
        Get the AgentMetricResult for the given metric and node name. 
        This is used to get the result of the metric computed during agent execution.

        Args:
            metric_name (string): The metric name
            node_name (string): The node name
        Return:
            agent_metric_result (AgentMetricResult): The AgentMetricResult object for the metric.
        """
        for metric in self.__online_metric_results:
            if metric.applies_to == "node" and metric.name == metric_name \
                    and metric.node_name == node_name and metric.interaction_id == get_current_trace_id():
                return metric

        return None

    def __reset_results(self):
        self.__online_metric_results.clear()
        self.__execution_counts.clear()
        self.__nodes_being_run.clear()
        trace_log_file_path = Path(
            f"{TRACE_LOG_FILE_PATH}/{TRACE_LOG_FILE_NAME}.log")
        with open(trace_log_file_path, "w") as file:
            # Wipe the log file
            pass

    def evaluate_context_relevance(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [
                                       ContextRelevanceMetric()
                                   ],
                                   compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing context relevance metric on an agentic node.

        For more details, see :class:`ibm_watsonx_gov.metrics.ContextRelevanceMetric`

        Args:
            func (Optional[Callable], optional): The node on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ContextRelevanceMetric() ].
            compute_online (Optional[bool], optional): The flag to indicate whether the metric should be computed along with the node execution or not.

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped node.

        Examples:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_context_relevance
                    def agentic_node(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = ContextRelevanceMetric(
                        method="sentence_bert_bge", threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(
                        method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_context_relevance(metrics=[metric_1, metric_2])
                    def agentic_node(*args, *kwargs):
                        pass
        """
        return ContextRelevanceDecorator(api_client=self.api_client,
                                         configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                         metric_results=self.__online_metric_results,
                                         execution_counts=self.__execution_counts,
                                         nodes_being_run=self.__nodes_being_run,
                                         lock=update_lock,
                                         compute_online=compute_online).evaluate_context_relevance(func, configuration=configuration, metrics=metrics)

    def evaluate_answer_similarity(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [
                                       AnswerSimilarityMetric()
                                   ],
                                   compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing answer similarity metric on an agentic node.

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerSimilarityMetric`

        Args:
            func (Optional[Callable], optional): The node on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ AnswerSimilarityMetric() ].
            compute_online (Optional[bool], optional): The flag to indicate whether the metric should be computed along with the node execution or not.

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped node.

        Examples:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_answer_similarity
                    def agentic_node(*args, *kwargs):
                        pass


            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AnswerSimilarityMetric(
                        method="token_k_precision", threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = AnswerSimilarityMetric(
                        method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_answer_similarity(metrics=[metric_1, metric_2])
                    def agentic_node(*args, *kwargs):
                        pass
        """

        return AnswerSimilarityDecorator(api_client=self.api_client,
                                         configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                         metric_results=self.__online_metric_results,
                                         execution_counts=self.__execution_counts,
                                         nodes_being_run=self.__nodes_being_run,
                                         lock=update_lock,
                                         compute_online=compute_online).evaluate_answer_similarity(func, configuration=configuration, metrics=metrics)

    def evaluate_faithfulness(self,
                              func: Optional[Callable] = None,
                              *,
                              configuration: Optional[AgenticAIConfiguration] = None,
                              metrics: list[GenAIMetric] = [
                                  FaithfulnessMetric()
                              ],
                              compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing faithfulness metric on an agentic node.

        For more details, see :class:`ibm_watsonx_gov.metrics.FaithfulnessMetric`

        Args:
            func (Optional[Callable], optional): The node on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ FaithfulnessMetric() ].
            compute_online (Optional[bool], optional): The flag to indicate whether the metric should be computed along with the node execution or not.

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped node.

        Examples:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_faithfulness
                    def agentic_node(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = FaithfulnessMetric(method="token_k_precision", threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = FaithfulnessMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_faithfulness(metrics=[metric_1, metric_2])
                    def agentic_node(*args, *kwargs):
                        pass
        """

        return FaithfulnessDecorator(api_client=self.api_client,
                                     configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                     metric_results=self.__online_metric_results,
                                     execution_counts=self.__execution_counts,
                                     nodes_being_run=self.__nodes_being_run,
                                     lock=update_lock,
                                     compute_online=compute_online).evaluate_faithfulness(func, configuration=configuration, metrics=metrics)

    def evaluate_unsuccessful_requests(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [
                                       UnsuccessfulRequestsMetric()
                                   ],
                                   compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing unsuccessful requests metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.UnsuccessfulRequestsMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ UnsuccessfulRequestsMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_unsuccessful_requests
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = UnsuccessfulRequestsMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_unsuccessful_requests(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        return UnsuccessfulRequestsDecorator(api_client=self.api_client,
                                         configuration=self.agentic_ai_configuration,
                                         metric_results=self.__online_metric_results,
                                         execution_counts=self.__execution_counts,
                                         nodes_being_run=self.__nodes_being_run,
                                         lock=update_lock,
                                         compute_online=compute_online).evaluate_unsuccessful_requests(func, configuration=configuration, metrics=metrics)

    def evaluate_answer_relevance(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [
                                       AnswerRelevanceMetric()
                                   ],
                                   compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing answer relevance metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerRelevanceMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ AnswerRelevanceMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_relevance
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AnswerRelevanceMetric(method="token_recall", threshold=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_relevance(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        return AnswerRelevanceDecorator(api_client=self.api_client,
                                         configuration=self.agentic_ai_configuration,
                                         metric_results=self.__online_metric_results,
                                         execution_counts=self.__execution_counts,
                                         nodes_being_run=self.__nodes_being_run,
                                         lock=update_lock,
                                         compute_online=compute_online).evaluate_answer_relevance(func, configuration=configuration, metrics=metrics)

    def evaluate_general_quality_with_llm(self,
                                          func: Optional[Callable] = None,
                                          *,
                                          configuration: Optional[AgenticAIConfiguration] = None,
                                          metrics: list[GenAIMetric] = [],
                                          compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing llm validation metric on an agentic node.

        For more details, see :class:`ibm_watsonx_gov.metrics.LLMValidationMetric`

        Args:
            func (Optional[Callable], optional): The node on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric]): The list of metrics to compute as part of this evaluator.
            compute_online (Optional[bool], optional): The flag to indicate whether the metric should be computed along with the node execution or not.
                                               When online is set to False, evaluate_metrics method should be invoked on the AgenticEvaluator to compute the metric.

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped node.

        Examples:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_general_quality_with_llm
                    def agentic_node(*args, *kwargs):
                        pass
        """
        return LLMValidationDecorator(api_client=self.api_client,
                                      configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                      metric_results=self.__online_metric_results,
                                      execution_counts=self.__execution_counts,
                                      nodes_being_run=self.__nodes_being_run,
                                      lock=update_lock,
                                      compute_online=compute_online).evaluate_general_quality_with_llm(func,
                                                                                                       configuration=configuration,
                                                                                                       metrics=metrics)

    def evaluate_tool_calling_hallucination(self,
                                            func: Optional[Callable] = None,
                                            *,
                                            configuration: Optional[AgenticAIConfiguration] = None,
                                            metrics: list[GenAIMetric] = [
                                                ToolCallingHallucinationMetric()
                                            ],
                                            compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing tool_calling_hallucination metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallingHallucinationMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallingHallucinationMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_tool_calling_hallucination
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds
                .. code-block:: python

                    metric_1 = ToolCallingHallucinationMetric(threshold=MetricThreshold(type="upper_limit", value=0.7))
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_tool_calling_hallucination(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        return ToolCallingHallucinationDecorator(api_client=self.api_client,
                                                 configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                                 metric_results=self.__online_metric_results,
                                                 execution_counts=self.__execution_counts,
                                                 nodes_being_run=self.__nodes_being_run,
                                                 lock=update_lock,
                                                 compute_online=compute_online).evaluate_tool_calling_hallucination(func, configuration=configuration, metrics=metrics)
    def evaluate_prompt_safety_risk(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [PromptSafetyRiskMetric()],
                                   compute_online: Optional[bool] = True,
                                   ) -> dict:
        
        """
        An evaluation decorator for computing prompt safety risk metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.PromptSafetyRiskMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ PromptSafetyRiskMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_prompt_safety_risk
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = PromptSafetyRiskMetric(method="prompt_injection_125m_0.7_en", thresholds=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = PromptSafetyRiskMetric(method="prompt_injection_125m_0.7_en", thresholds=MetricThreshold(type="lower_limit", value=0.7))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_prompt_safety_risk(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return PromptSafetyRiskDecorator(api_client=self.api_client,
                                        configuration=self.agentic_ai_configuration,
                                        metric_results=self.__online_metric_results,
                                        execution_counts=self.__execution_counts,
                                        nodes_being_run=self.__nodes_being_run,
                                        lock=update_lock,
                                        compute_online=compute_online).evaluate_prompt_safety_risk(func, configuration=configuration, metrics=metrics)
    

    def evaluate_hap(self,
                    func: Optional[Callable] = None,
                    *,
                    configuration: Optional[AgenticAIConfiguration] = None,
                    metrics: list[GenAIMetric] = [HAPMetric()],
                    compute_online: Optional[bool] = True,
                    ) -> dict:
        
        """
        An evaluation decorator for computing HAP metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.HAPMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [HAPMetric()].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_hap
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = hap(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    metric_2 = hap(thresholds=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_hap(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return HAPDecorator(api_client=self.api_client,
                            configuration=self.agentic_ai_configuration,
                            metric_results=self.__online_metric_results,
                            execution_counts=self.__execution_counts,
                            nodes_being_run=self.__nodes_being_run,
                            lock=update_lock,
                            compute_online=compute_online).evaluate_hap(func, configuration=configuration, metrics=metrics)
    
    def evaluate_pii(self,
                    func: Optional[Callable] = None,
                    *,
                    configuration: Optional[AgenticAIConfiguration] = None,
                    metrics: list[GenAIMetric] = [PIIMetric()],
                    compute_online: Optional[bool] = True,
                    ) -> dict:
        
        """
        An evaluation decorator for computing PII metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.PIIMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [PIIMetric()].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_pii
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = pii(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    metric_2 = pii(thresholds=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_pii(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return PIIDecorator(api_client=self.api_client,
                                                 configuration=self.agentic_ai_configuration,
                                                 metric_results=self.__online_metric_results,
                                                 execution_counts=self.__execution_counts,
                                                 nodes_being_run=self.__nodes_being_run,
                                                 lock=update_lock,
                                                 compute_online=compute_online).evaluate_pii(func, configuration=configuration, metrics=metrics)
    
    def evaluate_answer_quality(self,
                                func: Optional[Callable] = None,
                                *,
                                configuration: Optional[AgenticAIConfiguration] = None,
                                metrics: list[GenAIMetric] = MetricGroup.ANSWER_QUALITY.get_metrics(
                                ),
                                compute_online: Optional[bool] = True
                                ) -> dict:
        
        """
        An evaluation decorator for computing answer quality metrics on an agentic tool.
        Answer Quality metrics include Answer Relevance, Faithfulness, Answer Similarity, Unsuccessful Requests

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerRelevanceMetric`, :class:`ibm_watsonx_gov.metrics.FaithfulnessMetric`, 
        :class:`ibm_watsonx_gov.metrics.UnsuccessfulRequestsMetric`, see :class:`ibm_watsonx_gov.metrics.AnswerSimilarityMetric`,

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to MetricGroup.ANSWER_QUALITY.get_metrics().

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_quality
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = FaithfulnessMetric(thresholds=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = AnswerRelevanceMetric(method="token_recall", thresholds=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_quality(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return AnswerQualityDecorator(api_client=self.api_client,
                                    configuration=self.agentic_ai_configuration,
                                    metric_results=self.__online_metric_results,
                                    execution_counts=self.__execution_counts,
                                    nodes_being_run=self.__nodes_being_run,
                                    lock=update_lock,
                                    compute_online=compute_online).evaluate_answer_quality(func, configuration=configuration, metrics=metrics)

    def evaluate_content_safety(self,
                                func: Optional[Callable] = None,
                                *,
                                configuration: Optional[AgenticAIConfiguration] = None,
                                metrics: list[GenAIMetric] = MetricGroup.CONTENT_SAFETY.get_metrics(
                                ),
                                compute_online: Optional[bool] = True
                                ) -> dict:
        
        """
        An evaluation decorator for computing content safety metrics on an agentic tool.
        Content Safety metrics include Prompt Safety Risk, HAP, PII

        For more details, see :class:`ibm_watsonx_gov.metrics.PromptSafetyRiskMetric`, :class:`ibm_watsonx_gov.metrics.hap`, 
        :class:`ibm_watsonx_gov.metrics.pii`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to MetricGroup.CONTENT_SAFETY.get_metrics().

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_content_safety
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = PromptSafetyRiskMetric(method="prompt_injection_125m_0.7_en", thresholds=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = hap(thresholds=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_content_safety(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return ContentSafetyDecorator(api_client=self.api_client,
                                                 configuration=self.agentic_ai_configuration,
                                                 metric_results=self.__online_metric_results,
                                                 execution_counts=self.__execution_counts,
                                                 nodes_being_run=self.__nodes_being_run,
                                                 lock=update_lock,
                                                 compute_online=compute_online).evaluate_content_safety(func, configuration=configuration, metrics=metrics)