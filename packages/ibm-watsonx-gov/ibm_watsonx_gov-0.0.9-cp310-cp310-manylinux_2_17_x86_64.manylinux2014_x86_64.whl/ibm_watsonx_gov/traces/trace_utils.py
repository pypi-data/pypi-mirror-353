# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Generator, List

from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.entities.agentic_app import (AgenticApp,
                                                  MetricsConfiguration, Node)
from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.evaluation_result import AgentMetricResult
from ibm_watsonx_gov.evaluate.impl.evaluate_metrics_impl import \
    _evaluate_metrics
from ibm_watsonx_gov.traces.span_node import SpanNode
from ibm_watsonx_gov.traces.span_util import (get_attributes,
                                              get_span_nodes_from_json)
from ibm_watsonx_gov.utils.python_utils import add_if_unique, get

try:
    from opentelemetry.proto.trace.v1.trace_pb2 import Span
except:
    pass

TARGETED_TRACE_NAMES = [
    "openai.embeddings",
    "openai.chat",
    # TODO: check attributes for other frameworks as well.
    # Add additional names if more black box metrics need to be calculated
]
ONE_M = 1000000
COST_METADATA = {  # Costs per 1M tokens
    "openai": {
        "gpt-4o": {"input": 5.0, "output": 15.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        # Note: Added from web
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    },
    "anthropic": {
        "claude-3-opus": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
    },
    "google": {
        "gemini-1.5-pro": {"input": 7.0, "output": 21.0},
        "gemini-1.5-flash": {"input": 0.35, "output": 1.05},
    },
    "mistral": {
        "mistral-large": {"input": 8.0, "output": 24.0},
        "mistral-7b": {"input": 0.25, "output": 0.80},
        "mixtral-8x7b": {"input": 1.00, "output": 3.00},
    },
    "cohere": {
        "command-r": {"input": 1.00, "output": 3.00},
    },
    "ai21": {
        "jurassic-2": {"input": 10.0, "output": 20.0},
    },
}


class TraceUtils:

    @staticmethod
    def build_span_trees(spans: list) -> List[SpanNode]:
        root_spans: list[SpanNode] = []

        span_nodes: dict[str, SpanNode] = {}
        for span in spans:
            span_nodes.update(get_span_nodes_from_json(span))

        # Create tree
        for span_id, node in span_nodes.items():
            parent_id = node.span.parent_span_id
            if not parent_id:
                root_spans.append(node)  # Root span which will not have parent
            else:
                parent_node = span_nodes.get(parent_id)
                if parent_node:
                    parent_node.add_child(node)
                else:
                    # Orphan span where parent is not found
                    root_spans.append(node)

        return root_spans

    @staticmethod
    def convert_array_value(array_obj: Dict) -> List:
        """Convert OTEL array value to Python list"""
        return [
            item.get("stringValue")
            or int(item.get("intValue", ""))
            or float(item.get("doubleValue", ""))
            or bool(item.get("boolValue", ""))
            for item in array_obj.get("values", [])
        ]

    @staticmethod
    def stream_trace_data(file_path: Path) -> Generator:
        """Generator that yields spans one at a time."""
        with open(file_path) as f:
            for line in f:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse line: {line}\nError: {e}")

    @staticmethod
    def __prase_and_extract_meta_data(span, meta_data: dict) -> None:
        """
        Extract meta data required to calculate agent level metrics from spans
        """
        if span.name in TARGETED_TRACE_NAMES:
            attributes = get_attributes(span.attributes)
            provider = attributes.get("gen_ai.system")
            llm_type = attributes.get("llm.request.type")
            model = attributes.get("gen_ai.request.model")

            if not llm_type or not model:
                return

            cost_key = (provider, llm_type, model)
            meta_data["cost"].append(
                {
                    "provider_details": cost_key,
                    "total_prompt_tokens": attributes.get("gen_ai.usage.prompt_tokens", 0),
                    "total_completion_tokens": attributes.get(
                        "gen_ai.usage.completion_tokens", 0
                    ),
                    "total_tokens": attributes.get("llm.usage.total_tokens", 0),
                }
            )
            meta_data["input_token_count"].append(
                attributes.get("gen_ai.usage.prompt_tokens", 0))
            meta_data["output_token_count"].append(
                attributes.get("gen_ai.usage.completion_tokens", 0))

    @staticmethod
    def calculate_cost(usage_data: List[dict]) -> float:
        """Calculate cost for given list of usage."""
        total_cost = 0.0

        for data in usage_data:
            (provider, _, model) = data["provider_details"]
            provider = provider.lower()
            model = model.lower()

            try:
                model_pricing = COST_METADATA[provider][model]
            except KeyError:
                raise ValueError(
                    f"Pricing not available for {provider}/{model}")

            # Calculate costs (per 1M tokens)
            input_cost = (data["total_prompt_tokens"] /
                          ONE_M) * model_pricing["input"]
            output_cost = (data["total_completion_tokens"] / ONE_M) * model_pricing[
                "output"
            ]
            total_cost += input_cost + output_cost

        return total_cost

    @staticmethod
    def compute_metrics_from_trace(span_tree: SpanNode, api_client: APIClient = None) -> tuple[list[AgentMetricResult], list[Node], list]:
        metric_results, nodes_details, edges = [], [], []
        trace_metadata = defaultdict(list)

        agentic_app, nodes_config = None, {}
        if span_tree.agentic_app:
            agentic_app = AgenticApp.model_validate_json(span_tree.agentic_app)
            nodes_config = {
                n.name: n.metrics_configurations for n in agentic_app.nodes}

        interaction_id = span_tree.span.trace_id.hex()

        thread_id_key = "traceloop.association.properties.thread_id"
        conversation_id = get_attributes(span_tree.span.attributes, [
                                         thread_id_key]).get(thread_id_key) or interaction_id

        # Add Interaction level metrics
        metric_results.extend(TraceUtils.__compute_interaction_level_metrics(
            agentic_app, api_client, span_tree.span, interaction_id, conversation_id))

        # Add node level metrics result
        metric_results.extend(TraceUtils.__compute_node_level_metrics(
            span_tree.children, api_client, nodes_details, trace_metadata, nodes_config, interaction_id, conversation_id))

        return metric_results, nodes_details, edges

    @staticmethod
    def __compute_node_level_metrics(span_nodes: SpanNode, api_client, nodes_data, trace_metadata, nodes_config, interaction_id, conversation_id):
        metric_results = []
        node_stack = list(span_nodes)
        child_stack = list()
        while node_stack or child_stack:
            is_parent = not child_stack
            node = child_stack.pop() if child_stack else node_stack.pop()
            if is_parent:
                parent_span = node.span
                node_name, metrics_config_from_decorators, data, code_id = None, [], None, ""
            span = node.span

            for attr in span.attributes:
                key = attr.key
                value = attr.value.string_value

                if is_parent:
                    if key == "traceloop.entity.name":
                        node_name = value
                    elif key == "gen_ai.runnable.code_id":
                        code_id = value
                    elif key in ("traceloop.entity.input", "traceloop.entity.output"):
                        try:
                            content = json.loads(value)
                            inputs_outputs = content.get(
                                "inputs" if key.endswith("input") else "outputs")
                            if isinstance(inputs_outputs, str):
                                inputs_outputs = json.loads(inputs_outputs)
                            if data:
                                data.update(inputs_outputs)
                            else:
                                data = inputs_outputs
                        except (json.JSONDecodeError, AttributeError):
                            pass
                if key.startswith("wxgov.config.metrics"):
                    metrics_config_from_decorators.append(json.loads(value))

            if (not node_name) or (node_name == "__start__"):
                continue

            # Extract required details to calculate metrics from each span
            TraceUtils.__prase_and_extract_meta_data(span, trace_metadata)
            child_stack.extend(node.children)

            if not child_stack:
                metrics_to_compute, all_metrics_config = TraceUtils.__get_metrics_to_compute(
                    nodes_config, node_name, metrics_config_from_decorators)

                add_if_unique(Node(name=node_name, func_name=code_id.split(":")[-1] if code_id else node_name, metrics_configurations=all_metrics_config), nodes_data,
                              ["name", "func_name"])

                for mc in metrics_to_compute:
                    metric_result = _evaluate_metrics(configuration=mc.configuration, data=data,
                                                      metrics=mc.metrics, api_client=api_client).to_dict()
                    for mr in metric_result:
                        node_result = {
                            "applies_to": "node",
                            "interaction_id": interaction_id,
                            "node_name": node_name,
                            "conversation_id": conversation_id,
                            **mr
                        }

                        metric_results.append(AgentMetricResult(**node_result))

                # Add node latency metric result
                metric_results.append(AgentMetricResult(name="latency",
                                                        value=(int(
                                                            parent_span.end_time_unix_nano) - int(parent_span.start_time_unix_nano))/1e9,
                                                        group=MetricGroup.PERFORMANCE,
                                                        applies_to="node",
                                                        interaction_id=interaction_id,
                                                        conversation_id=conversation_id,
                                                        node_name=node_name))

                # Get the node level metrics computed online during graph invocation from events
                metric_results.extend(TraceUtils.__get_metrics_results_from_events(
                    events=parent_span.events,
                    interaction_id=interaction_id,
                    conversation_id=conversation_id,
                    node_name=node_name))

        metric_results.extend(
            TraceUtils.__extract_metrics_from_trace_metadata(trace_metadata, interaction_id, conversation_id))

        return metric_results

    @staticmethod
    def __compute_interaction_level_metrics(agentic_app, api_client, span, interaction_id, conversation_id) -> list[AgentMetricResult]:
        metric_results = []
        metric_results.append(AgentMetricResult(name="latency",
                                                value=(int(
                                                    span.end_time_unix_nano) - int(span.start_time_unix_nano))/1000000000,
                                                group=MetricGroup.PERFORMANCE,
                                                applies_to="interaction",
                                                interaction_id=interaction_id,
                                                conversation_id=conversation_id))
        if agentic_app:
            data = {}

            attrs = get_attributes(
                span.attributes, ["traceloop.entity.input", "traceloop.entity.output"])
            inputs = json.loads(
                attrs.get("traceloop.entity.input", {})).get("inputs", {})
            data.update(inputs)
            outputs = json.loads(
                attrs.get("traceloop.entity.output", {})).get("outputs", {})
            data.update(outputs)

            metric_result = _evaluate_metrics(configuration=agentic_app.metrics_configuration.configuration, data=data,
                                              metrics=agentic_app.metrics_configuration.metrics, api_client=api_client).to_dict()
            for mr in metric_result:
                node_result = {
                    "applies_to": "interaction",
                    "interaction_id": interaction_id,
                    "conversation_id": conversation_id,
                    **mr
                }

                metric_results.append(AgentMetricResult(**node_result))

        return metric_results

    @staticmethod
    def __get_metrics_to_compute(nodes_config, node_name, metrics_configurations):
        metrics_to_compute, all_metrics_config = [], []

        if nodes_config.get(node_name):
            metrics_config = nodes_config.get(node_name)
            for mc in metrics_config:
                mc_obj = MetricsConfiguration(
                    configuration=mc.configuration, metrics=mc.metrics)
                metrics_to_compute.append(mc_obj)
                all_metrics_config.append(mc_obj)

        for mc in metrics_configurations:
            mc_obj = MetricsConfiguration.model_validate(
                mc.get("metrics_configuration"))

            all_metrics_config.append(mc_obj)
            if mc.get("compute_online") == "false":
                metrics_to_compute.append(mc_obj)

        return metrics_to_compute, all_metrics_config

    @staticmethod
    def search_attribute(spans, attribute_name=None, attribute_prefix=None) -> list:
        """
        Recursively search for the attribute values in the given spans with the given attribute name or prefix.
        """
        attr_values = []
        if not spans or not (attribute_name or attribute_prefix):
            return attr_values

        for sp in spans:
            sp_node = sp.node.span
            for attr in sp_node.get("attributes"):
                if attribute_prefix:
                    if attr.get("key").startswith(attribute_prefix):
                        attr_values.append(json.loads(
                            get(attr, "value.stringValue")))
                elif attribute_name:
                    if attr.get("key") == attribute_name:
                        attr_values.append(json.loads(
                            get(attr, "value.stringValue")))
            if not attr_values:
                attr_values = TraceUtils.search_attribute(
                    sp.children, attribute_name, attribute_prefix)
        return attr_values

    @staticmethod
    def __get_metrics_results_from_events(events, interaction_id, conversation_id, node_name):
        results = []
        if not events:
            return results

        for event in events:
            for attr in event.attributes:
                if attr.key == "attr_wxgov.result.metric":
                    val = attr.value.string_value
                    if val:
                        mr = json.loads(val)
                        mr.update({
                            "node_name": node_name,
                            "interaction_id": interaction_id,
                            "conversation_id": conversation_id
                        })
                        results.append(AgentMetricResult(**mr))

        return results

    @staticmethod
    def __extract_metrics_from_trace_metadata(trace_metadata: dict, interaction_id: str, conversation_id: str) -> list:
        metrics_result = []

        for metric, data in trace_metadata.items():
            if metric == "cost":
                metric_value = TraceUtils.calculate_cost(data)
            elif metric == "input_token_count" or metric == "output_token_count":
                metric_value = sum(data)
            else:
                continue
            agent_mr = {
                "name": metric,
                "value": metric_value,
                "interaction_id": interaction_id,
                "applies_to": "interaction",
                "conversation_id": conversation_id,
                "group": MetricGroup.USAGE.value
            }

            metrics_result.append(AgentMetricResult(**agent_mr))

        return metrics_result
