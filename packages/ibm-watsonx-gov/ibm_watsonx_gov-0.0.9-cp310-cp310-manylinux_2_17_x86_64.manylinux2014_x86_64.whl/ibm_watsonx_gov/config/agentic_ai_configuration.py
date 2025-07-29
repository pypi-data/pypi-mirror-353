# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os
from typing import Annotated, Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from ibm_watsonx_gov.config.gen_ai_configuration import GenAIConfiguration
from ibm_watsonx_gov.entities.enums import EvaluatorFields


class OTLPCollectorConfiguration(BaseModel):
    """
    Configuration settings for the OpenTelemetry Protocol collector.
    """
    # TODO set a valid default value
    endpoint: Annotated[str | None, Field(title="OTLP Endpoint",
                                          description="The OTLP collector endpoint URL for sending trace data.",
                                          default="http://localhost:4318/v1/traces")]
    insecure: Annotated[bool | None, Field(title="Insecure Connection",
                                           description="Whether to disable TLS for the exporter (i.e., use an insecure connection).",
                                           default=False)]
    is_grpc: Annotated[bool | None, Field(title="Use gRPC",
                                          description="If True, use gRPC for exporting traces instead of HTTP.",
                                          default=False)]
    timeout: Annotated[int | None, Field(title="Timeout",
                                         description="Timeout in milliseconds for sending telemetry data to the collector.",
                                         default=100)]
    headers: Annotated[dict[str, str] | None, Field(title="Headers",
                                                    description="Headers needed to call the server.",
                                                    default_factory=dict)]


class TracingConfiguration(BaseModel):
    """
    The tracing configuration details. One of project_id or space_id is required.
    If the otlp_collector_config is provided, the traces are logged to server, otherwise the traces are logged to file on disk. 
    If its required to log the traces to both server and local file, provide the otlp_collector_config and set the flag log_traces_to_file to True.
    """
    project_id: Annotated[str | None, Field(title="Project ID",
                                            description="The project id.",
                                            default=None)]
    space_id: Annotated[str | None, Field(title="Space ID",
                                          description="The space id.",
                                          default=None)]
    resource_attributes: Annotated[dict[str, str]
                                   | None, Field(title="Resource Attributes",
                                                 description="The additional properties shared among spans.",
                                                 default_factory=dict)]
    otlp_collector_config: Annotated[OTLPCollectorConfiguration | None,
                                     Field(title="OTLP Collector Config",
                                           description="OTLP Collector configuration.",
                                           default=None)]
    log_traces_to_file: Annotated[bool | None, Field(
        title="Log Traces to file",
        description="The flag to enable logging of traces to a file. If set to True, the traces are logged to a file. Use the flag when its needed to log the traces to file and to be sent to the server simultaneously.",
        default=False)]

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        if not (self.project_id or self.space_id):
            raise ValueError(
                "The project or space id is required. Please provide one of them and retry.")

        return self

    @classmethod
    def create_from_env(cls):
        # TODO get the default value and validate the tracing url env variable
        tracing_url = os.getenv("WATSONX_TRACING_URL") or ""
        project_id = os.getenv("PROJECT_ID")
        space_id = os.getenv("SPACE_ID")

        return TracingConfiguration(
            tracing_url=tracing_url,
            project_id=project_id,
            space_id=space_id
        )

    @property
    def enable_server_traces(self) -> bool:
        # Check if otlp_collector_config field was set
        return self.otlp_collector_config is not None

    @property
    def enable_local_traces(self) -> bool:
        # if otlp_collector_config is not set, enable local traces
        return self.log_traces_to_file or self.otlp_collector_config is None


class AgenticAIConfiguration(GenAIConfiguration):
    """
    The configuration interface for Agentic AI tools and applications.
    """
    input_fields: Annotated[Optional[list[str]], Field(title="Input Fields",
                                                       description="The list of model input fields in the data.",
                                                       default=[],
                                                       examples=[["question", "context1", "context2"]])]

    interaction_id_field: Annotated[Optional[str], Field(title="Interaction id field",
                                                         description="The interaction identifier field name.",
                                                         examples=[
                                                             "interaction_id"],
                                                         default="interaction_id")]

    conversation_id_field: Annotated[Optional[str], Field(title="Conversation id field",
                                                          description="The conversation identifier field name.",
                                                          examples=[
                                                              "conversation_id"],
                                                          default="conversation_id")]

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        return self

    @classmethod
    def create_configuration(cls, *, app_config: Optional[Self],
                             method_config: Optional[Self],
                             defaults: list[EvaluatorFields],
                             add_record_fields: bool = True) -> Self:
        """
        Creates a configuration object based on the provided parameters.

        Args:
            app_config (Optional[Self]): The application configuration.
            method_config (Optional[Self]): The method configuration.
            defaults (list[EvaluatorFields]): The default fields to include in the configuration.
            add_record_fields (bool, optional): Whether to add record fields to the configuration. Defaults to True.

        Returns:
            Self: The created configuration object.
        """

        if method_config is not None:
            return method_config

        if app_config is not None:
            return app_config

        mapping = EvaluatorFields.get_default_fields_mapping()
        config = {field.value: mapping[field] for field in defaults}

        if not add_record_fields:
            return cls(**config)

        system_fields = [EvaluatorFields.RECORD_ID_FIELD,
                         EvaluatorFields.RECORD_TIMESTAMP_FIELD,
                         EvaluatorFields.INTERACTION_ID_FIELD,
                         EvaluatorFields.CONVERSATION_ID_FIELD]
        for field in system_fields:
            if field not in defaults:
                config[field.value] = EvaluatorFields.get_default_fields_mapping()[
                    field]
        return cls(**config)
