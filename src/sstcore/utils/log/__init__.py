"""
Install ready-to-use Log Pipeline

- Setup Loguru for console, .log and .json
- Handle calls from EventBus with LogDTOs
                                                       DependencyLevel[X]
"""

__all__: list[str] = [
    "LogParam",
    "setup_logging",
    "setup_minimal_logging",
    #
    "reset_log_result",
    "fetch_log_result",
    #
    "handle_log_event",
]

from ._event_handler import handle_log_event
from ._param import LogParam
from ._setup import (
    fetch_log_result,
    reset_log_result,
    setup_logging,
    setup_minimal_logging,
)
