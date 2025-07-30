from .tqdm import tqdm
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("islandkit")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0"

__all__ = ["tqdm"]
