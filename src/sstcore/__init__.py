# TODO: very good text
from importlib.metadata import PackageNotFoundError, version

from .utils.path import PathGuard
from .utils.print import printer

try:  # show pyproject.toml package name
    __version__: str = version("sstcore")
except PackageNotFoundError:
    __version__ = "unknown"


__all__: list[str] = [
    "__version__",
    "PathGuard",
    "printer",
]
