"""Exception hierarchy for Momentum SDK."""

from typing import Optional, Dict, Any


class MomentumError(Exception):
    """Base exception for all Momentum SDK errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or "MOMENTUM_ERROR"
        self.details = details or {}


class CompressionError(MomentumError):
    """Raised when compression fails."""

    def __init__(self, message: str, original_text: Optional[str] = None):
        super().__init__(message, code="COMPRESSION_ERROR")
        if original_text:
            self.details["original_length"] = len(original_text)


class ConfigurationError(MomentumError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, param: Optional[str] = None):
        super().__init__(message, code="CONFIG_ERROR")
        if param:
            self.details["parameter"] = param
