"""
Setup loguru for console, .log and .json

- Handle LogDTO from EventBus

"""

__all__: list[str] = [
    "LogParam",
    "setup_logging",
]
from .param import LogParam
from .setup import setup_logging
