import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import wraps

from loguru import logger


@dataclass
class DateRange:
    start: datetime | date = date(2026, 1, 1)
    end: datetime | date = date(2026, 12, 31)

    def __post_init__(self):
        if type(self.start) is not type(self.end):
            raise TypeError(
                f"start: {type(self.start)} must equal end:{type(self.end)}"
            )
        if self.start > self.end:  # TEST: fine without error?
            logger.warning("Start of daterange is after end, range inverted!")

    @property
    def date_type(self) -> type[datetime] | type[date]:
        return type(self.start)

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    # @property
    # LATER: string_duration, interval, others?


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start: float = time.perf_counter()
        result = func(*args, **kwargs)
        end: float = time.perf_counter()
        logger.info(f"Duration for '{func.__name__}': {end - start:.6f}s")
        return result

    return wrapper


def day_count(day: date | None = None) -> int:
    """Returns day of Millennium, relative to input or today"""
    day: date = day or date.today()
    delta: timedelta = day - date(2000, 1, 1)
    return delta.days
