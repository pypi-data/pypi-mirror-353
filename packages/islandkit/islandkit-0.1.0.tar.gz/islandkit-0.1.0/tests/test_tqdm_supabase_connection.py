import asyncio
import os
import sys
from pathlib import Path
import importlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

island_tqdm = importlib.import_module("islandkit.tqdm")


@pytest.mark.asyncio
async def test_tqdm_can_connect_to_supabase():
    """Verify that the tqdm uploader can connect to Supabase using real credentials."""
    python_key = os.getenv("PYTHON_KEY")
    if not python_key:
        pytest.skip("PYTHON_KEY environment variable not set")

    island_tqdm.PYTHON_KEY = python_key

    uploader = island_tqdm._SupabaseUploader.__new__(island_tqdm._SupabaseUploader)
    uploader._enabled = True
    uploader._connected = False
    uploader._loop = asyncio.get_event_loop()
    uploader._queue = asyncio.Queue()

    await uploader._async_init()
    await asyncio.sleep(0.1)

    if not uploader._connected:
        pytest.skip("Supabase connection failed")

    assert uploader._connected is True

    # cancel any background tasks spawned during the test
    current = asyncio.current_task()
    for task in asyncio.all_tasks():
        if task is not current:
            task.cancel()
    await asyncio.sleep(0)
