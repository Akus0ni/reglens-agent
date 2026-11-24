"""OpenTelemetry to the RegLens Aspire dashboard (spec 0001, R1.17, P6; D3).

LangChain/LangGraph spans come from the Traceloop instrumentation (prompts and completions recorded unless
TRACELOOP_TRACE_CONTENT=false). The httpx instrumentation adds ``traceparent`` to MCP requests, so RegLens's ASP.NET
Core spans join the same trace.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.langchain import LangchainInstrumentor
from opentelemetry.instrumentation.langchain.callback_handler import TraceloopCallbackHandler
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE_NAME = "reglens-agent"


def _ignore(*_: object, **__: object) -> None:
    return None


# LangGraph 1.2 sends its graph lifecycle events (on_interrupt, on_resume) to every callback handler, although its
# docs say only GraphCallbackHandler subclasses get them. Traceloop's handler (0.63.1) has neither method, and every
# interrupt logged an AttributeError. They carry nothing the trace needs.
for _event in ("on_interrupt", "on_resume"):
    if not hasattr(TraceloopCallbackHandler, _event):
        setattr(TraceloopCallbackHandler, _event, _ignore)


@contextmanager
def telemetry(endpoint: str) -> Iterator[trace.Tracer]:
    """Exports spans while the block runs and flushes them at the end. An empty endpoint turns export off."""
    if not endpoint:
        yield trace.get_tracer(SERVICE_NAME)
        return

    provider = TracerProvider(resource=Resource.create({"service.name": SERVICE_NAME}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True)))
    trace.set_tracer_provider(provider)
    HTTPXClientInstrumentor().instrument()
    LangchainInstrumentor().instrument()
    try:
        yield trace.get_tracer(SERVICE_NAME)
    finally:
        provider.shutdown()
