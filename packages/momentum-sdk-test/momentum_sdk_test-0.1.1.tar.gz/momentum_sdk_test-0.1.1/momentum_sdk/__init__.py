"""
Momentum SDK - Lightweight interface to Momentum's prompt compression engine.

Usage:
    from momentum import compress, stats, MomentumError

    compressed = compress(prompt, context="gpt-4o")
    meta = stats(compressed)
"""

from .config import settings
from .exceptions import MomentumError

__version__ = "0.1.1"


def configure(api_key: str, mode: str = "remote", **kwargs):
    """
    Configure the Momentum SDK.
    
    Args:
        api_key: Your Momentum API key
        mode: "remote" or "local"
        **kwargs: Additional configuration options
    """
    settings.api_key = api_key
    settings.mode = mode
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

# Dynamic import based on mode
if settings.mode == "local":
    from .core import compress, stats
else:  # remote
    # Import but don't instantiate client until compress/stats is called
    from . import client
    compress = client.compress
    stats = client.stats

__all__ = ["compress", "stats", "configure", "MomentumError"]
