"""
Momentum SDK - Lightweight interface to Momentum's prompt compression engine.

Usage:
    from momentum import compress, stats, MomentumError

    compressed = compress(prompt, context="gpt-4o")
    meta = stats(compressed)
"""

from .config import settings
from .exceptions import MomentumError

__version__ = "0.1.0"

# Dynamic import based on mode
if settings.mode == "local":
    from .core import compress, stats
else:  # remote
    from .client import compress, stats

__all__ = ["compress", "stats", "MomentumError"]
