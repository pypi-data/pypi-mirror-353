# islandkit/config.py
"""Configuration management utilities.
Configuration is read from environment variables when available,
otherwise the user is prompted for input."""

import os
import sys
from typing import Optional


# Default Supabase configuration
SUPABASE_URL = "https://wuifbgugznzwpdzzdsqv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1aWZiZ3Vnem56d3Bkenpkc3F2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5NzIwMTAsImV4cCI6MjA2MjU0ODAxMH0.UXOpL4eSFf-mKtCmfbHR3uOAhhmsDYgYuYkrkMYhVe0"


def _is_interactive_environment() -> bool:
    """Check whether the current environment supports user interaction.

    Supported environments include:
    - Real TTY terminals
    - PyCharm run configuration
    - VS Code terminals
    - Jupyter environments

    Returns:
        bool: ``True`` if input can be requested.
    """
    # Method 1: standard TTY check
    if sys.stdin.isatty():
        return True

    # Method 2: look for IDE related environment variables
    ide_indicators = [
        "PYCHARM_HOSTED",  # set by PyCharm
        "JETBRAINS_IDE",  # generic JetBrains marker
        "VSCODE_PID",  # VS Code
        "JPY_PARENT_PID",  # Jupyter
        "JUPYTER_RUNTIME_DIR",  # Jupyter
        "SPYDER_ARGS",  # Spyder
        "THEIA_WORKSPACE_ROOT",  # Theia IDE
    ]

    for indicator in ide_indicators:
        if os.getenv(indicator):
            return True

    # Method 3: detect IPython shells
    try:
        import IPython

        if IPython.get_ipython() is not None:
            return True
    except ImportError:
        pass

    return False


def _get_python_key_from_input() -> Optional[str]:
    """Prompt the user for ``PYTHON_KEY`` on the command line."""
    try:
        print("\n[islandkit] 📋 未检测到 PYTHON_KEY 环境变量")
        print("[islandkit] 💡 您可以在终端中设置环境变量：")
        print("    export ISLANDKIT_PYTHON_KEY='您的key'")
        print("[islandkit] 或者现在直接输入（回车跳过）：")

        key = input("[islandkit] 请输入 PYTHON_KEY: ").strip()

        if not key:
            print("[islandkit] ⏭️ 已跳过输入，将以离线模式运行")
            return None

        print("[islandkit] ✅ PYTHON_KEY 已设置")
        return key

    except (KeyboardInterrupt, EOFError):
        print("\n[islandkit] ⏭️ 输入已取消，将以离线模式运行")
        return None
    except Exception as exc:
        print(f"[islandkit] ⚠️ 输入过程中出现错误: {exc}")
        print("[islandkit] ⏭️ 将以离线模式运行")
        return None


def get_python_key() -> Optional[str]:
    """Retrieve the ``PYTHON_KEY`` setting.

    Priority:
    1. environment variable ``ISLANDKIT_PYTHON_KEY``
    2. command-line input
    3. return ``None`` to run offline

    Returns:
        Optional[str]: The key or ``None``
    """
    # First try to read from the environment
    env_key = os.getenv("ISLANDKIT_PYTHON_KEY")
    if env_key:
        print("[islandkit] ✅ 从环境变量读取到 PYTHON_KEY")
        return env_key.strip()

    # Skip prompting when not interactive
    if not _is_interactive_environment():
        print("[islandkit] ℹ️ 非交互式环境，跳过 PYTHON_KEY 输入，以离线模式运行")
        return None

    # Fetch from command line
    return _get_python_key_from_input()


def get_config() -> dict:
    """Return the complete configuration dictionary."""
    return {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": SUPABASE_KEY,
        "PYTHON_KEY": get_python_key(),
    }


# Exported configuration helpers
__all__ = ["get_config", "get_python_key", "SUPABASE_URL", "SUPABASE_KEY"]
