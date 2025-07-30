#!/usr/bin/env python3

import os
from pathlib import Path

# Set environment variables for testing
os.environ["MOMENTUM_MODE"] = "local"
os.environ["MOMENTUM_API_KEY"] = "test-api-key"

# Set the path to the engine library
project_root = Path(__file__).parent.parent
engine_lib_path = (
    project_root / "core_engine" / "target" / "release" / "libmomentum_engine.so"
)
os.environ["MOMENTUM_ENGINE_LIB_PATH"] = str(engine_lib_path)


def test_sdk():
    """Test the Momentum SDK functionality."""
    # Import the SDK
    from momentum_sdk import compress, stats

    print("✅ Successfully imported Momentum SDK")

    # Print engine library path for debugging
    print(f"🔍 Looking for engine at: {os.environ.get('MOMENTUM_ENGINE_LIB_PATH')}")

    # Test compression
    test_prompt = "Hello world, this is a test prompt for Momentum SDK! Let's see how well the compression works with some longer text content that would benefit from compression."
    print(f"📝 Original prompt: {test_prompt}")

    # Compress the text - this should fail if the engine isn't available
    compressed = compress(test_prompt, context="gpt-4o")
    print(f"🗜️  Compressed to: {len(compressed)} characters")

    # Get statistics
    statistics = stats(compressed)
    print(f"📊 Stats: {statistics}")

    # Verify stats values
    assert "original_tokens" in statistics, "Missing original_tokens in stats"
    assert "compressed_tokens" in statistics, "Missing compressed_tokens in stats"
    assert "compression_ratio" in statistics, "Missing compression_ratio in stats"
    assert "bytes_saved" in statistics, "Missing bytes_saved in stats"
    assert statistics["compression_ratio"] > 0, "Invalid compression ratio"

    print("✅ All stats fields present and valid")


if __name__ == "__main__":
    print("🧪 Testing Momentum SDK\n")
    test_sdk()
    print("\n🎉 Tests completed!")
