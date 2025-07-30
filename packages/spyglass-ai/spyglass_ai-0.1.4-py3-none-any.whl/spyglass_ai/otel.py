import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

class SpyglassOtelError(Exception):
    """Base exception for Spyglass OpenTelemetry configuration errors."""
    pass

class ExporterConfigurationError(SpyglassOtelError):
    """Raised when exporter configuration is invalid."""
    pass

def _create_exporter():
    """Create and return an OTLP gRPC span exporter based on environment variables."""
    # Allow configuration of OTLP endpoint via environment variable
    endpoint = os.getenv("SPYGLASS_OTEL_EXPORTER_OTLP_ENDPOINT")
    headers = os.getenv("SPYGLASS_OTEL_EXPORTER_OTLP_HEADERS")
    
    kwargs = {}
    kwargs["insecure"] = True # TODO: Make this configurable
    if not endpoint:
        raise ExporterConfigurationError("SPYGLASS_OTEL_EXPORTER_OTLP_ENDPOINT is not set")
    kwargs["endpoint"] = endpoint
    if headers:
        try:
            # Parse headers string like "key1=value1,key2=value2"
            parsed_headers = {}
            for header_pair in headers.split(","):
                header_pair = header_pair.strip()
                if not header_pair:
                    continue
                if "=" not in header_pair:
                    raise ValueError(f"Invalid header format: '{header_pair}' (missing '=')")
                key, value = header_pair.split("=", 1)
                parsed_headers[key.strip()] = value.strip()
            kwargs["headers"] = parsed_headers
        except ValueError as e:
            raise ExporterConfigurationError(
                f"Invalid headers format: {headers}. Expected format: 'key1=value1,key2=value2'"
            ) from e
    
    return OTLPSpanExporter(**kwargs)

# Create the tracer provider and exporter
provider = TracerProvider()
exporter = _create_exporter()
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
spyglass_tracer = trace.get_tracer("spyglass-tracer")