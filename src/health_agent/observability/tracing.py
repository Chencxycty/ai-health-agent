import os
import sys
from functools import lru_cache

from opentelemetry import trace
from opentelemetry.instrumentation.httpx import (
    HTTPXClientInstrumentor,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)


_initialized = False


def setup_tracing() -> None:
    global _initialized

    if _initialized:
        return

    resource = Resource.create(
        {
            "service.name": os.getenv(
                "OTEL_SERVICE_NAME",
                "ai-health-agent",
            ),
            "service.version": "0.3.0",
        }
    )

    provider = TracerProvider(resource=resource)

    processor = BatchSpanProcessor(ConsoleSpanExporter(out=sys.__stdout__))

    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    HTTPXClientInstrumentor().instrument()

    _initialized = True


@lru_cache
def get_tracer():
    return trace.get_tracer("health_agent")
