import functools
from typing import Any

from loguru import logger
from rich import print as rich_print

from ..color import ColorBox

# REFACTOR: check what remains useful after events established


def debug_log_or_print(anyway: bool = False):
    """Check class attributes for log or print then scan args and kwargs"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            def _render(t: Any) -> str:
                return f"{type(t).__name__}: {t}"

            is_debug: bool = getattr(self, "_debug", False)
            is_log: bool = getattr(self, "_log", False)

            if is_debug or anyway:
                _target_str = f"Func={func.__name__}"
                _args_str = f"args=({', '.join([_render(a) for a in args])})"
                _kwargs_str = (
                    f"kwargs=({ {k: _render(v) for k, v in kwargs.items()} })"
                )
                if is_log:  # opt(depth=1) fixes Loguru's stack frame lookup
                    logger.opt(depth=1).error(
                        f"{_target_str} | {_args_str} | {_kwargs_str}"
                    )
                else:
                    c: ColorBox = ColorBox.bold()
                    _info = [
                        c.red(_target_str),
                        c.cyan(_args_str),
                        c.yellow(_kwargs_str),
                    ]
                    if console := getattr(self, "console", None):
                        console.print("\n".join(_info))
                    else:
                        rich_print("\n".join(_info))

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
