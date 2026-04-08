from collections.abc import Callable

from .monitor import main as monitor
from .setup import attach_callback, logger_catch

# LATER: import args as entire block?

__all__: list[Callable] = [
    monitor,
    # TEST: setup stuff fine here?
    logger_catch,
    attach_callback,
]
