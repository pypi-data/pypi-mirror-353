# Momentum SDK

Lightweight Python SDK for Momentum's prompt compression engine.

## Installation

```bash
pip install momentum-sdk
```

## Quick Start

```python
from momentum import compress, decompress, stats

# Compress a prompt
compressed = compress("Your long prompt here...", context="gpt-4o")

# Feed to your model
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": compressed}]
)

# Decompress if needed
original = decompress(compressed)

# Get compression stats
meta = stats(compressed)
print(f"Saved {meta['bytes_saved']} bytes ({meta['compression_ratio']:.2f}x compression)")
```

## Configuration

### Environment Variables

```bash
# Required
export MOMENTUM_API_KEY="sk_live_..."

# Optional
export MOMENTUM_MODE="remote"  # or "local"
export MOMENTUM_API_BASE_URL="https://api.momentum.ai"
export MOMENTUM_TELEMETRY="disabled"  # or "enabled"
```

### Configuration Files

The SDK looks for configuration in these locations (in order):
1. `~/.momentum/config.json` or `~/.momentum/config.yaml`
2. `.momentum.json` or `.momentum.yaml` in current directory
3. Environment variables

Example config file:
```json
{
  "api_key": "sk_live_...",
  "mode": "remote",
  "cache_enabled": true,
  "cache_ttl_seconds": 3600
}
```

## API Reference

### compress(prompt, context="gpt-4o", binary=False)

Compress a prompt for efficient token usage.

**Arguments:**
- `prompt` (str): Text to compress
- `context` (str): Target model context (e.g., "gpt-4o", "claude-3")
- `binary` (bool): If True, return raw bytes; if False, return text-safe string

**Returns:** Compressed prompt ready to feed to the model

### decompress(compressed)

Restore original prompt from compressed version.

**Arguments:**
- `compressed` (str): Compressed text from compress()

**Returns:** Original prompt text

### stats(compressed)

Get detailed compression metrics.

**Arguments:**
- `compressed` (str): Compressed text from compress()

**Returns:** Dictionary with:
- `original_tokens`: Token count before compression
- `compressed_tokens`: Token count after compression
- `compression_ratio`: Ratio of compression achieved
- `bytes_saved`: Difference in UTF-8 byte length
- `estimated_cost_usd`: Approximate cost savings
- `model`: Context argument used
- `mode`: Execution path used ("local" or "remote")
- `timestamp`: ISO-8601 UTC timestamp

## Modes

### Remote Mode (default)
Uses Momentum's hosted compression service. No setup required.

### Local Mode
Uses embedded Rust engine for zero-latency compression. Requires:
1. Install SDK with native extensions: `pip install momentum-sdk[local]`
2. Set mode: `export MOMENTUM_MODE=local`

## Error Handling

```python
from momentum import compress, MomentumError

try:
    compressed = compress(prompt)
except MomentumError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
    print(f"Details: {e.details}")
```

## Telemetry

The SDK can send anonymous usage metrics via OpenTelemetry:

```bash
export MOMENTUM_TELEMETRY=enabled
export MOMENTUM_TELEMETRY_ENDPOINT=https://otel-collector.example.com
```

## Development

```bash
# Clone the repo
git clone https://github.com/momentum-ai/momentum-core
cd momentum-core/sdk

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black momentum_sdk tests
ruff momentum_sdk tests
```

## License

MIT 