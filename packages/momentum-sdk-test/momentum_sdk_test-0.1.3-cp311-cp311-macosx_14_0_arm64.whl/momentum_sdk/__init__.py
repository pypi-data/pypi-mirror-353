"""
Momentum SDK - Prompt compression engine.

Usage:
    from momentum_sdk import compress, stats, MomentumError

    compressed = compress(prompt, context="gpt-4o")
    meta = stats(compressed)
"""

from .exceptions import MomentumError
from .core import compress, stats

__version__ = "0.1.3"

__all__ = ["compress", "stats", "MomentumError"]
