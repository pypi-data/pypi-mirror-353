"""Local compression implementation using Rust FFI."""

# Removing unused os import
# import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, cast, List
from datetime import datetime
import os
from cffi import FFI  # type: ignore

from .config import settings
from .exceptions import CompressionError, ConfigurationError
from .telemetry import instrument, telemetry


# Global FFI instance
ffi: Optional[FFI] = None


class RustEngine:
    """Wrapper for Rust compression engine."""

    def __init__(self):
        self._lib = None
        self._load_ffi()
        self._load_library()

    def _load_ffi(self):
        """Load FFI definitions."""
        global ffi
        if ffi is not None:
            return

        ffi = FFI()
        ffi.cdef(
            """
            typedef struct {
                char* compressed;
                int original_tokens;
                int compressed_tokens;
                float compression_ratio;
                int bytes_saved;
                float estimated_cost_usd;
                char* model;
                char* mode;
                char* timestamp;
                char* error;
            } CompressionResult;
            
            CompressionResult* momentum_compress(const char* prompt, const char* context, bool binary);
            char* momentum_decompress(const char* compressed);
            CompressionResult* momentum_stats(const char* compressed);
            void momentum_free_result(CompressionResult* result);
            void momentum_free_string(char* str);
            """
        )

    def _load_library(self):
        """Load the Rust shared library."""
        if ffi is None:
            raise RuntimeError("FFI not initialized")

        # Try to find the library
        lib_name = {
            "darwin": "libmomentum_engine.dylib",
            "linux": "libmomentum_engine.so",
            "win32": "momentum_engine.dll",
        }.get(sys.platform)

        if not lib_name:
            raise ConfigurationError(f"Unsupported platform: {sys.platform}")

        # Search paths
        search_paths: List[Path] = []

        # Custom path from settings or environment variable (highest priority)
        if settings.engine_lib_path:
            search_paths.append(Path(settings.engine_lib_path))

        # Check if running in GitHub Actions
        if os.environ.get("GITHUB_WORKSPACE"):
            github_workspace = Path(os.environ["GITHUB_WORKSPACE"])
            search_paths.extend(
                [
                    github_workspace / "sdk" / "momentum_sdk" / "lib" / lib_name,
                    github_workspace / "core_engine" / "target" / "release" / lib_name,
                ]
            )

        # Relative to SDK package
        sdk_dir = Path(__file__).parent
        search_paths.extend(
            [
                sdk_dir / lib_name,
                sdk_dir / "lib" / lib_name,
                sdk_dir.parent / "lib" / lib_name,
            ]
        )

        # System paths
        search_paths.extend(
            [
                Path("/usr/local/lib") / lib_name,
                Path("/usr/lib") / lib_name,
            ]
        )

        # Development path (when running from source)
        project_root = sdk_dir.parent.parent
        search_paths.append(
            project_root / "core_engine" / "target" / "release" / lib_name
        )

        # Additional paths for CI environments
        ci_paths = [
            Path(os.getcwd()) / "momentum_sdk" / "lib" / lib_name,
            Path(os.getcwd()) / "lib" / lib_name,
            Path(os.getcwd()).parent / "core_engine" / "target" / "release" / lib_name,
        ]
        search_paths.extend(ci_paths)

        # Print search paths for debugging
        print(f"Searching for engine library {lib_name} in:")
        for path in search_paths:
            print(f"  - {path} (exists: {path.exists()})")

        # Try to load
        for path in search_paths:
            if path.exists():
                try:
                    self._lib = ffi.dlopen(str(path))
                    print(f"Successfully loaded engine from: {path}")
                    return
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
                    continue

        # Failed to load
        paths_str = "\n  ".join(str(p) for p in search_paths)
        raise ConfigurationError(
            f"Failed to load Momentum engine library. Searched in:\n  {paths_str}\n"
            f"Set MOMENTUM_ENGINE_LIB_PATH environment variable to specify the location."
        )

    def compress(
        self, prompt: str, context: str = "gpt-4o", binary: bool = False
    ) -> tuple[str, Dict[str, Any]]:
        """Compress using Rust engine."""
        start_time = time.time()

        if ffi is None:
            raise RuntimeError("FFI not initialized")

        # Call Rust function
        result = self._lib.momentum_compress(
            prompt.encode("utf-8"), context.encode("utf-8"), binary
        )

        if result == ffi.NULL:
            raise CompressionError("Compression returned null", original_text=prompt)

        try:
            # Check for error
            if result.error != ffi.NULL:
                error_msg = ffi.string(result.error)
                error_str = cast(bytes, error_msg).decode("utf-8")
                raise CompressionError(error_str, original_text=prompt)

            # Extract compressed text
            if result.compressed == ffi.NULL:
                raise CompressionError("No compressed output", original_text=prompt)

            compressed_bytes = ffi.string(result.compressed)
            compressed = cast(bytes, compressed_bytes).decode("utf-8")

            # Extract stats
            stats = {
                "original_tokens": result.original_tokens,
                "compressed_tokens": result.compressed_tokens,
                "compression_ratio": result.compression_ratio,
                "bytes_saved": result.bytes_saved,
                "estimated_cost_usd": result.estimated_cost_usd,
                "model": (
                    cast(bytes, ffi.string(result.model)).decode("utf-8")
                    if result.model != ffi.NULL
                    else context
                ),
                "mode": (
                    cast(bytes, ffi.string(result.mode)).decode("utf-8")
                    if result.mode != ffi.NULL
                    else "local"
                ),
                "timestamp": (
                    cast(bytes, ffi.string(result.timestamp)).decode("utf-8")
                    if result.timestamp != ffi.NULL
                    else datetime.utcnow().isoformat() + "Z"
                ),
            }

            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            telemetry.record_compression(
                stats["original_tokens"],
                stats["compressed_tokens"],
                duration_ms,
                context,
            )

            return compressed, stats

        finally:
            # Free memory
            if ffi is not None:
                self._lib.momentum_free_result(result)

    def decompress(self, compressed: str) -> str:
        """Decompress using Rust engine."""
        if ffi is None:
            raise RuntimeError("FFI not initialized")

        # Call Rust function
        result = self._lib.momentum_decompress(compressed.encode("utf-8"))

        if result == ffi.NULL:
            raise CompressionError("Decompression failed", original_text=compressed)

        try:
            original = cast(bytes, ffi.string(result)).decode("utf-8")
            return original
        finally:
            # Free memory
            if ffi is not None:
                self._lib.momentum_free_string(result)

    def stats(self, compressed: str) -> Dict[str, Any]:
        """Get stats using Rust engine."""
        if ffi is None:
            raise RuntimeError("FFI not initialized")

        # Call Rust function
        result = self._lib.momentum_stats(compressed.encode("utf-8"))

        if result == ffi.NULL:
            raise CompressionError("Failed to get stats")

        try:
            # Check for error
            if result.error != ffi.NULL:
                error_msg = cast(bytes, ffi.string(result.error)).decode("utf-8")
                raise CompressionError(error_msg)

            # Extract stats
            return {
                "original_tokens": result.original_tokens,
                "compressed_tokens": result.compressed_tokens,
                "compression_ratio": result.compression_ratio,
                "bytes_saved": result.bytes_saved,
                "estimated_cost_usd": result.estimated_cost_usd,
                "model": (
                    cast(bytes, ffi.string(result.model)).decode("utf-8")
                    if result.model != ffi.NULL
                    else "unknown"
                ),
                "mode": (
                    cast(bytes, ffi.string(result.mode)).decode("utf-8")
                    if result.mode != ffi.NULL
                    else "local"
                ),
                "timestamp": (
                    cast(bytes, ffi.string(result.timestamp)).decode("utf-8")
                    if result.timestamp != ffi.NULL
                    else datetime.utcnow().isoformat() + "Z"
                ),
            }

        finally:
            # Free memory
            if ffi is not None:
                self._lib.momentum_free_result(result)


# Global engine instance
_engine: Optional[RustEngine] = None


def _get_engine() -> RustEngine:
    """Get or create engine instance."""
    global _engine
    if _engine is None:
        _engine = RustEngine()
    return _engine


@instrument
def compress(prompt: str, context: str = "gpt-4o", binary: bool = False) -> str:
    """
    Compress a prompt using local Rust engine.

    Args:
        prompt: Text to compress
        context: Target model context (e.g., "gpt-4o", "claude-3")
        binary: If True, return raw bytes; if False, return text-safe string

    Returns:
        Compressed prompt ready to feed to the model

    Raises:
        CompressionError: If compression fails
        ConfigurationError: If engine library cannot be loaded
    """
    engine = _get_engine()
    compressed, _ = engine.compress(prompt, context, binary)
    return compressed


@instrument
def stats(compressed: str) -> Dict[str, Any]:
    """
    Get compression statistics.

    Args:
        compressed: Compressed text from compress()

    Returns:
        Dictionary with compression metrics (see client.stats for schema)
    """
    engine = _get_engine()
    return engine.stats(compressed)
