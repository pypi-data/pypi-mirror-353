# IslandKit

Your TQDM on dynamic island - Remote progress tracking for Python long-running tasks.

## Overview

IslandKit is a small Python library that extends the [tqdm](https://github.com/tqdm/tqdm) progress bar so that updates can be broadcast in real time via Supabase Realtime. This allows you to monitor the progress of long-running jobs such as data processing or model training remotely on an iOS device.

### Key Features

- Fully compatible drop-in replacement for `tqdm`
- Progress updates are sent to a private Supabase channel
- Works in both synchronous and asynchronous code
- Configuration via environment variables, JSON config file or directly in code
- Optional Python key authentication

## Installation

Install the package from PyPI:

```bash
pip install islandkit
```

For development install from the repository:

```bash
pip install -e .
```

## Usage

### Basic Example

```python
import asyncio
from islandkit import tqdm

async def main():
    # Optionally configure Supabase credentials here
    for i in tqdm(range(100), desc="Processing"):
        await asyncio.sleep(0.1)

asyncio.run(main())
```

### Model Training Example

Check `examples/` for a more complete training demo using `tqdm` with additional metrics.

## Configuration

The library reads configuration from environment variables or `~/.islandkit/config.json` if it exists. At minimum you need the Supabase URL, an anon key and optionally a Python key for authentication.

Environment variables:

```
ISLANDKIT_PYTHON_KEY=your-python-key
```

## Development

Run `pytest` to execute any tests and `black` to format the code. The project targets Python 3.8 and later.

## License

This project is released under the MIT License.

Contributions are welcome!
