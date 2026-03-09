"""Composition of frequently used generalized functions, utils and tools"""

# TODO: check docstring

from importlib.metadata import PackageNotFoundError, version
import logging

try:  # Show pyproject.toml package name
    __version__ = version("silvasta")
except PackageNotFoundError:
    __version__ = "unknown"

# Default logger for entire library, override after import if needed
logger: logging.Logger = logging.getLogger(__name__)

# Silent fail if no logger is configured in parent app
logger.addHandler(logging.NullHandler())

__all__: list = []
