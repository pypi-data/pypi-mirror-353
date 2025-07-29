# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
from functools import partial
from typing import Callable, Optional

from ibm_watsonx_gov.config.agentic_ai_configuration import \
    AgenticAIConfiguration
from ibm_watsonx_gov.entities.enums import EvaluatorFields
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.metrics.base_metric_decorator import BaseMetricDecorator
from ibm_watsonx_gov.metrics.tool_calling_hallucination.tool_calling_hallucination_metric import \
    ToolCallingHallucinationMetric
from ibm_watsonx_gov.utils.python_utils import parse_functions_to_schema
from wrapt import decorator


class ToolCallingHallucinationDecorator(BaseMetricDecorator):
    def evaluate_tool_calling_hallucination(self,
                                            func: Optional[Callable] = None,
                                            *,
                                            configuration: Optional[AgenticAIConfiguration] = None,
                                            metrics: list[GenAIMetric] = [
                                                ToolCallingHallucinationMetric()
                                            ]
                                            ) -> dict:
        """
        An evaluation decorator for computing tool calling hallucination metric on an agentic node.
        """
        if func is None:
            return partial(self.evaluate_tool_calling_hallucination, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.validate(func=func, metrics=metrics,
                              valid_metric_types=(ToolCallingHallucinationMetric,))

                metric_inputs = [
                    EvaluatorFields.QUESTION_FIELD
                ]
                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                if isinstance(configuration.tools, list) and all(callable(item) for item in configuration.tools):
                    configuration.tools = self.__get_tools_list_schema(
                        configuration.tools)

                original_result = self.compute_helper(func=func, args=args, kwargs=kwargs,
                                                      configuration=configuration,
                                                      metrics=metrics,
                                                      metric_inputs=metric_inputs,
                                                      metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating context relevance metric on {func.__name__},") from ex

        return wrapper(func)

    def __get_tools_list_schema(self, tools: list) -> list:
        """
        Convert the list of callable objects to the 
        format needed for the TCH computation

        Args:
            tools (list): List of Callable objects

        Returns:
            list: List of dictionary containing the tool
            specifications
        """
        tools_specifications = []
        for func in tools:
            tool_schema = parse_functions_to_schema(func)
            if not tool_schema:
                continue
            tools_specifications.append(tool_schema)

        return tools_specifications
