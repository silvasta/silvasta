"""
Setup loguru for console, .log and .json

- Handle LogDTO from EventBus

"""

__all__: list[str] = [
    "LogParam",
    "LogSetupResult",
    "setup_logging",
]
from .param import LogParam, LogSetupResult
from .setup import setup_logging
