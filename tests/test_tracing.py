from opentelemetry import trace

from health_agent.observability.tracing import (
    get_tracer,
    setup_tracing,
)


def test_setup_tracing() -> None:
    setup_tracing()

    provider = (
        trace.get_tracer_provider()
    )

    assert provider is not None


def test_setup_tracing_twice() -> None:
    setup_tracing()
    setup_tracing()

    provider = (
        trace.get_tracer_provider()
    )

    assert provider is not None


def test_get_tracer() -> None:
    setup_tracing()

    tracer = get_tracer()

    assert tracer is not None


def test_create_span() -> None:
    setup_tracing()

    tracer = get_tracer()

    with tracer.start_as_current_span(
        "test.span"
    ) as span:
        span.set_attribute(
            "test.value",
            123,
        )

        assert span is not None

        assert span.is_recording()

from opentelemetry.trace import (
    Status,
    StatusCode,
)


def test_record_exception() -> None:
    setup_tracing()

    tracer = get_tracer()

    with tracer.start_as_current_span(
        "test.error"
    ) as span:
        try:
            raise ValueError(
                "test error"
            )

        except ValueError as exc:
            span.record_exception(
                exc
            )

            span.set_status(
                Status(
                    StatusCode.ERROR,
                    str(exc),
                )
            )

            assert (
                span.status.status_code
                == StatusCode.ERROR
            )