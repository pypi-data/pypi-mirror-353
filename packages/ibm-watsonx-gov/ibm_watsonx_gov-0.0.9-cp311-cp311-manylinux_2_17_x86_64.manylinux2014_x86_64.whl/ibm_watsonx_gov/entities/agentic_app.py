
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from json import loads
from typing import Annotated, Optional

from pydantic import BaseModel, Field, TypeAdapter, field_serializer
from typing_extensions import Annotated

from ibm_watsonx_gov.config.agentic_ai_configuration import \
    AgenticAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.metrics import METRICS_UNION


class MetricsConfiguration(BaseModel):
    """
    The class representing the metrics to be computed and the configuration details required for them.
    """
    configuration: Annotated[AgenticAIConfiguration, Field(
        title="Metrics configuration", description="The configuration of the metrics to compute.")]
    metrics: Annotated[Optional[list[GenAIMetric]], Field(
        title="Metrics", description="The list of metrics to compute.", default=[])]
    metric_groups: Annotated[Optional[list[MetricGroup]], Field(
        title="Metric Groups", description="The list of metric groups to compute.", default=[])]

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if "metrics" in obj:
            obj["metrics"] = [TypeAdapter(METRICS_UNION).validate_python(
                m) for m in obj.get("metrics")]
        return super().model_validate(obj, **kwargs)

    @field_serializer("metrics", when_used="json")
    def metrics_serializer(self, metrics: list[GenAIMetric]):
        return [metric.model_dump(mode="json") for metric in metrics]


class Node(BaseModel):
    """
    The class representing a node in an agentic application.
    """
    name: Annotated[str, Field(
        title="Node name", description="The name of the node.")]
    func_name: Annotated[Optional[str], Field(
        title="Node function name", description="The name of the node function.", default=None)]
    metrics_configurations: Annotated[list[MetricsConfiguration], Field(
        title="Metrics configuration", description="The list of metrics and their configuration details.", default=[])]

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if "metrics_configurations" in obj:
            obj["metrics_configurations"] = [MetricsConfiguration.model_validate(
                m) for m in obj.get("metrics_configurations")]
        return super().model_validate(obj, **kwargs)


class AgenticApp(BaseModel):
    """
    The class representing an agentic application.
    An agent is composed of a set of nodes.
    """
    name: Annotated[str, Field(
        title="Agentic application name", description="The name of the agentic application.", default="Agent App")]
    metrics_configuration: Annotated[Optional[MetricsConfiguration], Field(
        title="Metrics configuration", description="The list of metrics to be computed on the agentic application and their configuration details.", default=None)]
    nodes: Annotated[Optional[list[Node]], Field(
        title="Node details", description="The nodes details.", default=[])]

    @classmethod
    def model_validate_json(cls, json_data, **kwargs):
        data = loads(json_data)
        if "metrics_configuration" in data:
            data["metrics_configuration"] = MetricsConfiguration.model_validate(
                data.get("metrics_configuration"))
        if "nodes" in data:
            data["nodes"] = [Node.model_validate(node)
                             for node in data.get("nodes", [])]
        return cls.model_validate(data, **kwargs)
