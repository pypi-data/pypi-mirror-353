# islandkit/tqdm.py
"""A thin wrapper fully compatible with :class:`tqdm.tqdm` that
also broadcasts progress to Supabase Realtime.

Usage::
    from islandkit import tqdm
    for _ in tqdm(range(1000)):
        ...
"""

import asyncio
import base64
import json
import threading
from typing import Optional, Any, Dict, Tuple
import copy
import time

from tqdm import tqdm as _tqdm
from supabase import create_async_client
from realtime import RealtimeChannelOptions, RealtimeSubscribeStates

from .config import get_config

# Load configuration from the settings module
try:
    _config = get_config()
    SUPABASE_URL = _config["SUPABASE_URL"]
    SUPABASE_KEY = _config["SUPABASE_KEY"]
    PYTHON_KEY = _config["PYTHON_KEY"]
except Exception as exc:
    print(f"[islandkit] ⚠️ 配置加载失败: {exc}")
    print("[islandkit] ℹ️ 将以离线模式运行，tqdm功能正常可用")
    SUPABASE_URL = None
    SUPABASE_KEY = None
    PYTHON_KEY = None


def _decode_python_key(encoded_key: str) -> tuple[Optional[str], Optional[str]]:
    """Decode a Base64 PythonKey exported from iOS into ``(access, refresh)``."""
    try:
        decoded = base64.b64decode(encoded_key)
        data = json.loads(decoded)
        return data["access"], data["refresh"]
    except Exception as exc:
        print(f"[islandkit] ❌ PythonKey 解码失败: {exc}")
        return None, None


# --------------- 后台上传器 --------------- #
class _SupabaseUploader:
    """Runs in a background thread; connects to Supabase and sends progress."""

    def __init__(self) -> None:
        # Skip starting the background thread when configuration is missing
        if not all([SUPABASE_URL, SUPABASE_KEY, PYTHON_KEY]):
            print("[islandkit] ℹ️ 缺少必要配置，跳过 Supabase 连接，以离线模式运行")
            self._enabled = False
            return

        self._enabled = True
        self._connected = False  # track connection state
        self._loop = asyncio.new_event_loop()
        self._queue: Optional[asyncio.Queue[dict]] = (
            None  # created later in the background loop
        )
        self._thread = threading.Thread(
            target=self._run_loop, name="islandkit-supabase", daemon=True
        )
        self._thread.start()

    # ---- external API ----
    def send(self, payload: dict) -> None:
        """Called from the main thread; put any JSON serialisable payload into the async queue."""
        if not self._enabled or self._queue is None:
            return
        try:
            asyncio.run_coroutine_threadsafe(self._queue.put(payload), self._loop)
        except Exception as exc:
            print(f"[islandkit] ⚠️ 进度队列发送失败: {exc}")

    # ---- internal ----
    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        # Queue must belong to the background event loop to avoid cross-loop errors
        self._queue = asyncio.Queue()
        self._loop.create_task(self._async_init())
        self._loop.run_forever()

    async def _async_init(self) -> None:
        """Establish the Supabase connection and start the consumer coroutine."""
        print("[islandkit] 🔐 开始解码 PythonKey...")
        access, refresh = _decode_python_key(PYTHON_KEY)
        if not (access and refresh):
            print("[islandkit] ❌ 无效 PythonKey，停止上传功能")
            print("[islandkit] ⚠️ tqdm 功能仍然正常可用，只是无法同步到远程")
            return

        # Retry mechanism: attempt connection up to three times
        for attempt in range(3):
            try:
                print(f"[islandkit] 📡 正在连接 Supabase... (尝试 {attempt + 1}/3)")
                self._client = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
                print("[islandkit] 🔑 正在设置用户会话...")
                await self._client.auth.set_session(access, refresh)
                sess = await self._client.auth.get_session()
                if not sess or not sess.user:
                    print("[islandkit] ❌ 会话设置失败，停止上传功能")
                    print("[islandkit] ⚠️ tqdm 功能仍然正常可用，只是无法同步到远程")
                    return
                # 成功连接，跳出重试循环
                break
            except Exception as exc:
                print(f"[islandkit] ⚠️ 连接尝试 {attempt + 1} 失败: {exc}")
                if attempt < 2:  # will retry
                    print("[islandkit] 🔄 retrying in 5 seconds...")
                    await asyncio.sleep(5)
                else:  # 最后一次尝试失败
                    print(
                        "[islandkit] ❌ all connection attempts failed, stopping uploads"
                    )
                    print("[islandkit] ⚠️ tqdm still works locally but will not sync")
                    return

        user_id = sess.user.id
        print(f"[islandkit] 👤 user ID: {user_id}")
        print("[islandkit] 📺 setting up Realtime channel...")

        try:
            self._channel = self._client.channel(
                f"tqdm:{user_id}",
                RealtimeChannelOptions(config={"private": True}),
            )

            def _on_subscribe(status, err):
                if status == RealtimeSubscribeStates.SUBSCRIBED:
                    print("[islandkit] ✅ connected to Supabase Realtime")
                    self._connected = True  # mark connection success
                    # start upload loop once subscribed
                    self._loop.create_task(self._upload_loop())
                elif status == RealtimeSubscribeStates.CLOSED:
                    print("[islandkit] ⚠️ Realtime connection closed")
                    self._connected = False
                elif err:
                    print(f"[islandkit] ⚠️ Realtime subscription failed: {err}")
                    self._connected = False

            # Run subscription in a background task without blocking
            sub_task = self._loop.create_task(self._channel.subscribe(_on_subscribe))

            # 10 second timeout; switch to offline mode if not connected
            async def _timeout_check() -> None:
                await asyncio.sleep(10)
                if not self._connected and not sub_task.done():
                    print("[islandkit] ⚠️ Realtime 订阅超时（10秒），改为离线模式")
                    sub_task.cancel()

            self._loop.create_task(_timeout_check())
        except Exception as exc:
            print(f"[islandkit] ❌ failed to configure Realtime channel: {exc}")
            print("[islandkit] ⚠️ will keep trying in the background; tqdm still works")

    async def _upload_loop(self) -> None:
        print("[islandkit] 🔄 starting progress upload loop")
        while True:
            try:
                payload = await self._queue.get()
                await self._channel.send_broadcast("tqdm", payload)
            except Exception as exc:
                print(f"[islandkit] ⚠️ 发送进度失败: {exc}")
                # small delay before retrying on failure
                await asyncio.sleep(1)


# Global singleton: start on import
print("[islandkit] 🚀 starting Supabase background connection...")
_uploader = _SupabaseUploader()


# --------------- custom tqdm --------------- #
class tqdm(_tqdm):
    """Full subclass of :class:`tqdm.tqdm`; syncs progress to Supabase on update and close."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_postfix: Dict[str, Any] = {}
        self._last_sent_payload: Optional[dict] = None

    def update(self, n: int = 1) -> None:
        super().update(n)
        self._maybe_send()

    def close(self) -> None:
        self._maybe_send(final=True)
        super().close()

    def set_postfix(self, ordered_dict=None, refresh=True, **kwargs):
        # UI update first
        super().set_postfix(ordered_dict, refresh, **kwargs)
        # Merge new postfix values
        new_postfix: Dict[str, Any] = {}
        if ordered_dict:
            new_postfix.update(ordered_dict)
        new_postfix.update(kwargs)
        self._current_postfix = new_postfix
        # Send combined payload
        self._maybe_send()

    # ---- internal ----
    def _maybe_send(self, final: bool = False) -> None:
        """
        1. Send progress as a percentage or count
        2. Include ``postfix`` if present
        3. Avoid sending duplicate payloads
        """
        try:
            # Build detailed payload
            payload = {
                "n": self.n,
                "total": self.total,
                "percent": round(self.n / self.total * 100, 1) if self.total else None,
                "elapsed": self.format_dict.get("elapsed"),
                "rate": self.format_dict.get("rate"),
                "eta": self.format_dict.get("remaining"),
                "unit": self.unit,
                "desc": self.desc,
            }
            if self._current_postfix:
                payload["postfix"] = copy.deepcopy(self._current_postfix)
            if final:
                payload["final"] = True

            if payload != self._last_sent_payload:
                _uploader.send(payload)
                self._last_sent_payload = payload
        except Exception:
            # Silently ignore upload errors to keep tqdm functional
            pass


# ---- expose ``tqdm`` for ``from islandkit import tqdm`` convenience ----
__all__ = ["tqdm"]
