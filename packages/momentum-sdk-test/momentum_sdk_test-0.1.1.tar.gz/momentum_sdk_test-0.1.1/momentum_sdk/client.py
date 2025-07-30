"""Remote client implementation for Momentum SDK."""

import time
from typing import Dict, Any, Optional
import httpx

from . import __version__

from .config import settings
from .exceptions import (
    MomentumError,
    CompressionError,
    NetworkError,
    AuthenticationError,
    RateLimitError,
)
from .telemetry import instrument, telemetry


class MomentumClient:
    """HTTP client for remote compression service."""

    def __init__(self):
        if not settings.api_key:
            raise AuthenticationError(
                "API key is required. Set it via environment variable MOMENTUM_API_KEY, "
                "or create a config file at ~/.momentum/config.json with your API key."
            )
        
        self.client = httpx.Client(
            base_url=settings.api_url,
            headers={
                "Authorization": f"Bearer {settings.api_key}",
                "User-Agent": f"momentum-sdk/{__version__}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(settings.timeout_seconds),
        )
        self._cache: Dict[str, Any] = {}

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and errors."""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise AuthenticationError()
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(retry_after=int(retry_after) if retry_after else None)
        elif response.status_code >= 500:
            raise NetworkError(
                f"Server error: {response.status_code}", endpoint=str(response.url)
            )
        else:
            try:
                error_data = response.json()
                raise MomentumError(
                    error_data.get("message", f"API error: {response.status_code}"),
                    code=error_data.get("code", "API_ERROR"),
                    details=error_data.get("details", {}),
                )
            except Exception:
                raise MomentumError(f"API error: {response.status_code}")

    def _retry_request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Execute request with retry logic."""
        last_error = None

        for attempt in range(settings.max_retries):
            try:
                response = self.client.request(method, path, **kwargs)
                return response
            except httpx.TimeoutException as e:
                last_error = NetworkError(f"Request timeout: {e}", endpoint=path)
            except httpx.NetworkError as e:
                last_error = NetworkError(f"Network error: {e}", endpoint=path)

            if attempt < settings.max_retries - 1:
                # Exponential backoff
                time.sleep(2**attempt)

        if last_error:
            raise last_error
        raise NetworkError("Max retries exceeded", endpoint=path)

    def compress(
        self, prompt: str, context: str = "gpt-4o", binary: bool = False
    ) -> str:
        """Compress prompt via API."""
        # Check cache
        cache_key = f"compress:{hash(prompt)}:{context}"
        if settings.cache_enabled and cache_key in self._cache:
            cached = self._cache[cache_key]
            if cached["expires_at"] > time.time():
                return cached["result"]

        response = self._retry_request(
            "POST",
            "/compress",
            json={"prompt": prompt, "context": context, "binary": binary},
        )

        data = self._handle_response(response)
        result = data["compressed"]

        # Update cache
        if settings.cache_enabled:
            self._cache[cache_key] = {
                "result": result,
                "expires_at": time.time() + settings.cache_ttl_seconds,
            }

        # Record metrics
        if "stats" in data:
            stats = data["stats"]
            telemetry.record_compression(
                stats["original_tokens"],
                stats["compressed_tokens"],
                stats.get("duration_ms", 0),
                context,
            )

        return result

    def stats(self, compressed: str) -> Dict[str, Any]:
        """Get compression stats via API."""
        response = self._retry_request(
            "POST", "/stats", json={"compressed": compressed}
        )

        data = self._handle_response(response)
        return data["stats"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


# Global client instance
_client: Optional[MomentumClient] = None


def _get_client() -> MomentumClient:
    """Get or create client instance."""
    global _client
    if _client is None:
        _client = MomentumClient()
    return _client


@instrument
def compress(prompt: str, context: str = "gpt-4o", binary: bool = False) -> str:
    """
    Compress a prompt using remote compression service.

    Args:
        prompt: Text to compress
        context: Target model context (e.g., "gpt-4o", "claude-3")
        binary: If True, return raw bytes; if False, return text-safe string

    Returns:
        Compressed prompt ready to feed to the model

    Raises:
        CompressionError: If compression fails
        NetworkError: If network request fails
        AuthenticationError: If API key is invalid
    """
    try:
        client = _get_client()
        return client.compress(prompt, context, binary)
    except MomentumError:
        raise
    except Exception as e:
        raise CompressionError(f"Compression failed: {e}", original_text=prompt)


@instrument
def stats(compressed: str) -> Dict[str, Any]:
    """
    Get compression statistics.

    Args:
        compressed: Compressed text from compress()

    Returns:
        Dictionary with compression metrics:
        - original_tokens: Estimated tokens in original text
        - compressed_tokens: Tokens in compressed text
        - compression_ratio: Ratio of compressed to original (lower is better)
        - bytes_saved: Bytes saved through compression
        - estimated_cost_usd: Estimated cost saving (USD)
        - model: Target model used for compression
        - mode: Compression mode used
        - timestamp: When compression was performed

    Raises:
        MomentumError: If retrieving stats fails
        NetworkError: If network request fails
    """
    try:
        client = _get_client()
        return client.stats(compressed)
    except MomentumError:
        raise
    except Exception as e:
        raise MomentumError(f"Failed to get stats: {e}")
