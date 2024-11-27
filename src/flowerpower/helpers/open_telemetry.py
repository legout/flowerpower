# If you wanted to use another OpenTelemetry destination such as the open-source Jaeger,
# setup the container locally and use the following code

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import Resource, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Add more open telemetry exporters here


def init_tracer(
    name: str,
    host: str = "localhost",
    port: int = 6831,
):
    jaeger_exporter = JaegerExporter(
        agent_host_name=host,  # Replace with your Jaeger agent host
        agent_port=port,  # Replace with your Jaeger agent port
    )

    span_processor = SimpleSpanProcessor(jaeger_exporter)
    provider = TracerProvider(
        active_span_processor=span_processor,
        resource=Resource.create({"service.name": f"flowerpower.{name}"}),
    )
    trace.set_tracer_provider(provider)

    return trace
