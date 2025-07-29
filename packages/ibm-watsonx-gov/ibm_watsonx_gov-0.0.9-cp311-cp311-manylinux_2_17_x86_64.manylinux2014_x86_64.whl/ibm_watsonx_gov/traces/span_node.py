# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

try:
    from opentelemetry.proto.trace.v1.trace_pb2 import Span
except:
    pass


class SpanNode:
    """
    Class to represent the structure of a single span and its children.
    """

    def __init__(self, service_name: str, agentic_app, span):
        self.service_name = service_name
        self.agentic_app = agentic_app
        self.span = span
        self.children: list['SpanNode'] = []

    def add_child(self, child: 'SpanNode'):
        self.children.append(child)

    def __repr__(self, level=0):
        indent = "  " * level
        s = f"{indent}- {self.span.name} (span_id={self.span.span_id.hex()}, parent_id={self.span.parent_span_id.hex() if self.span.parent_span_id else 'None'})\n"
        for child in self.children:
            s += child.__repr__(level + 1)
        return s
