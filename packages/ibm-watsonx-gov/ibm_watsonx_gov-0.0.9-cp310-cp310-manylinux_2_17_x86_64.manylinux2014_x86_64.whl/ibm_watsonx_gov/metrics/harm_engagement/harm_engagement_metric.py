# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Literal

import pandas as pd
from pydantic import Field

from ibm_watsonx_gov.config.gen_ai_configuration import GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.detectors_provider import DetectorsProvider

HARM_ENGAGEMENT = "harm_engagement"

class HarmEngagementResult(RecordMetricResult):
    name: str = HARM_ENGAGEMENT
    group: MetricGroup = MetricGroup.CONTENT_SAFETY


class HarmEngagementMetric(GenAIMetric):
    name: Annotated[Literal["harm_engagement"],
                    Field(default=HARM_ENGAGEMENT)]
    method: Annotated[
        Literal["granite_guardian"],
        Field(description=f"The method used to compute harm engagement metric.",
              default="granite_guardian")]
    tasks: Annotated[list[TaskType], Field(
        default=TaskType.values(), frozen=True)]
    is_reference_free: Annotated[bool, Field(default=False)]
    thresholds: Annotated[list[MetricThreshold], Field(default=[MetricThreshold(
        type="lower_limit", value=0.7)])]
    group: Annotated[MetricGroup, Field(
        default=MetricGroup.CONTENT_SAFETY, frozen=True)]

    def evaluate(
            self,
            data: pd.DataFrame | dict,
            configuration: GenAIConfiguration,
            **kwargs
        ) -> list[AggregateMetricResult]:

        kwargs["detector_params"] = {"risk": HARM_ENGAGEMENT}
        provider = DetectorsProvider(configuration=configuration,
                                     metric_name=self.name,
                                     metric_method=self.method,
                                     metric_group=self.group,
                                     thresholds=self.thresholds,
                                     **kwargs)
        aggregated_metric_result = provider.evaluate(data=data)
        return aggregated_metric_result
