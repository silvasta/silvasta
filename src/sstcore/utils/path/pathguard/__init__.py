from loguru import logger

logger.remove()  # NEXT: check how cli looks without that


class PathGuard:
    """Centralized path enforcement toolkit"""

    _debug = True

    @classmethod
    def debug(cls, toggle: bool | None = None):
        cls._debug: bool = not cls._debug if toggle is None else toggle
