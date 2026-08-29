"""
Collect helper for time related functions

- stays in fromat due to small size and relevance
                                                          PackageLevel[0]
"""

__all__: list[str] = [
    "DateRange",
    "timer",
    "day_count",
    "nice_duration",
]

import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import wraps

from loguru import logger

# LATER: check utc for entire project, maybe pendulum or stay with builtin


@dataclass
class DateRange:
    """Hold timespan and provide basic operations and information"""

    start: datetime | date = date(2026, 1, 1)
    end: datetime | date = date(2026, 12, 31)

    def __post_init__(self):
        if type(self.start) is not type(self.end):
            raise TypeError(
                f"start: {type(self.start)} must equal end:{type(self.end)}"
            )
        if self.start > self.end:
            logger.warning("Start of daterange is after end, range inverted!")

    @property
    def date_type(self) -> type[datetime] | type[date]:
        """Show type of internal date type"""
        # LATER: as class parameter
        return type(self.start)

    @property
    def duration(self) -> timedelta:
        """Show length of timespan"""
        return self.end - self.start


def timer(func):
    """Decorate function and Log execution time"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Launching timer")
        start: float = time.perf_counter()
        result = func(*args, **kwargs)
        end: float = time.perf_counter()
        logger.info(f"Duration for '{func.__name__}': {end - start:.6f}s")
        return result

    return wrapper


def day_count(day: date | None = None) -> int:
    """Calculate Day of Millennium for today or target day"""
    day: date = day or date.today()
    delta: timedelta = day - date(2000, 1, 1)
    return delta.days


def nice_duration(start: datetime, end: datetime) -> str:
    """Format duration with days, hours, minutes and seconds char"""

    duration: timedelta = end - start
    days: int = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m {seconds}s"
