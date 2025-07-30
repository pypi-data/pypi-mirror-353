"""OpenTelemetry instrumentation for Momentum SDK."""

from contextlib import contextmanager
from typing import Optional, Dict, Any
from functools import wraps
import time

# Add type ignores for imports that might not be available
from opentelemetry import trace, metrics

try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter  # type: ignore
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource  # type: ignore
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor  # type: ignore

    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False

from .config import settings


class TelemetryManager:
    """Manages OpenTelemetry setup and instrumentation."""

    def __init__(self):
        self.tracer: Optional[trace.Tracer] = None
        self.meter: Optional[metrics.Meter] = None
        self._initialized = False

        # Metrics
        self.compression_counter: Optional[metrics.Counter] = None
        self.decompression_counter: Optional[metrics.Counter] = None
        self.compression_duration: Optional[metrics.Histogram] = None
        self.compression_ratio: Optional[metrics.Histogram] = None
        self.bytes_saved: Optional[metrics.Histogram] = None

    def initialize(self):
        """Initialize telemetry if enabled."""
        if (
            settings.telemetry != "enabled"
            or self._initialized
            or not TELEMETRY_AVAILABLE
        ):
            return

        # Create resource with service info
        # Use type ignore for Resource since mypy has trouble with it
        resource = Resource.create(  # type: ignore[attr-defined]
            {
                "service.name": "momentum-sdk",
                "service.version": "0.1.0",
            }
        )

        # Setup tracing
        if settings.telemetry_endpoint:
            trace_exporter = OTLPSpanExporter(
                endpoint=f"{settings.telemetry_endpoint}/v1/traces"
            )
            trace_provider = TracerProvider(resource=resource)
            trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
            trace.set_tracer_provider(trace_provider)
            self.tracer = trace.get_tracer("momentum-sdk")

            # Setup metrics
            metric_reader = PeriodicExportingMetricReader(
                exporter=OTLPMetricExporter(
                    endpoint=f"{settings.telemetry_endpoint}/v1/metrics"
                ),
                export_interval_millis=60000,  # 1 minute
            )
            meter_provider = MeterProvider(
                resource=resource, metric_readers=[metric_reader]
            )
            metrics.set_meter_provider(meter_provider)
            self.meter = metrics.get_meter("momentum-sdk")

            # Create metrics
            self.compression_counter = self.meter.create_counter(
                "momentum.compressions",
                description="Number of compression operations",
                unit="1",
            )
            self.decompression_counter = self.meter.create_counter(
                "momentum.decompressions",
                description="Number of decompression operations",
                unit="1",
            )
            self.compression_duration = self.meter.create_histogram(
                "momentum.compression.duration",
                description="Duration of compression operations",
                unit="ms",
            )
            self.compression_ratio = self.meter.create_histogram(
                "momentum.compression.ratio",
                description="Compression ratio achieved",
                unit="1",
            )
            self.bytes_saved = self.meter.create_histogram(
                "momentum.bytes_saved",
                description="Bytes saved by compression",
                unit="By",
            )

            # Instrument HTTP client
            HTTPXClientInstrumentor().instrument()

            self._initialized = True

    @contextmanager
    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Create a span if telemetry is enabled."""
        if self.tracer:
            with self.tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                yield span
        else:
            yield None

    def record_compression(
        self,
        original_tokens: int,
        compressed_tokens: int,
        duration_ms: float,
        model: str,
    ):
        """Record compression metrics."""
        if not self._initialized:
            return

        ratio = compressed_tokens / original_tokens if original_tokens > 0 else 0
        saved = original_tokens - compressed_tokens

        attributes = {"model": model}

        if self.compression_counter:
            self.compression_counter.add(1, attributes)
        if self.compression_duration:
            self.compression_duration.record(duration_ms, attributes)
        if self.compression_ratio:
            self.compression_ratio.record(ratio, attributes)
        if self.bytes_saved:
            # Rough estimation: 1 token ≈ 4 bytes
            self.bytes_saved.record(saved * 4, attributes)

    def record_decompression(self, duration_ms: float):
        """Record decompression metrics."""
        if self.decompression_counter:
            self.decompression_counter.add(1)


# Global telemetry instance
telemetry = TelemetryManager()


def instrument(func):
    """Decorator to instrument functions with telemetry."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        telemetry.initialize()

        start_time = time.time()
        with telemetry.span(f"momentum.{func.__name__}") as span:
            try:
                result = func(*args, **kwargs)
                if span:
                    span.set_status(trace.Status(trace.StatusCode.OK))
                return result
            except Exception as e:
                if span:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000

                # Record specific metrics based on function
                if func.__name__ == "compress" and "result" in locals():
                    # Extract metrics from result if available
                    pass
                elif func.__name__ == "decompress":
                    telemetry.record_decompression(duration_ms)

    return wrapper
