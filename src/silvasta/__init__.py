import logging
from importlib.metadata import PackageNotFoundError, version

try:  # Show pyproject.toml package name
    __version__: str = version("silvasta")
except PackageNotFoundError:
    __version__ = "unknown"


# Default logger for entire library, override after import if needed
# TASK: somehow swich for loguru
logger: logging.Logger = logging.getLogger(__name__)
# Silent fail if no logger is configured in parent app
logger.addHandler(logging.NullHandler())

__all__: list = []
