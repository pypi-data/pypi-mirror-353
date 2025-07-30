"""Simple telemetry for Momentum SDK local operations."""

from contextlib import contextmanager
from typing import Optional, Dict, Any
from functools import wraps
import time


class TelemetryManager:
    """Simple telemetry manager for local operations."""

    def __init__(self):
        self._initialized = False

    def initialize(self):
        """Initialize telemetry - no-op for local mode."""
        self._initialized = True

    @contextmanager
    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Create a span context - no-op for local mode."""
        yield None

    def record_compression(
        self,
        original_tokens: int,
        compressed_tokens: int,  
        duration_ms: float,
        model: str,
    ):
        """Record compression metrics - no-op for local mode."""
        pass

    def record_decompression(self, duration_ms: float):
        """Record decompression metrics - no-op for local mode."""
        pass


# Global telemetry instance
telemetry = TelemetryManager()


def instrument(func):
    """Decorator to instrument functions - simplified for local mode."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        telemetry.initialize()
        return func(*args, **kwargs)

    return wrapper
