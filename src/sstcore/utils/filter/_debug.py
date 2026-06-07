import functools

from loguru import logger


def debug_log(func):
    """Decorator: Log target_set and corresponding class attributes!"""

    @functools.wraps(func)
    def wrapper(self, target_set, *args, **kwargs):
        if self._debug:
            attr_name: str = func.__name__.replace("fulfills_", "")
            attr_value: set | None = getattr(self, attr_name, None)
            logger.debug(f"{attr_name}={attr_value}, {target_set=}")
        return func(self, target_set, *args, **kwargs)

    return wrapper
