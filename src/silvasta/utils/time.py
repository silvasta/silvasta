from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import wraps

from loguru import logger


@dataclass
class DateRange:
    # IMPORTANT: how to extend this to be universal useful?
    # - TimeRange, DateRange, DateTimeRange?
    # - or simply 1 class that provides all?
    # TASK:
    # - Add some functions and checks here! (duration, interval, ...)

    start: datetime | date = date(2026, 1, 1)
    end: datetime | date = date(2026, 12, 31)

    @property
    def date_type(self) -> type[datetime] | type[date]:
        return type(self.start)

    # TODO: check for start < end? otherwise..
    # - could work that range is opposed
    def __post_init__(self):
        if type(self.start) is not type(self.end):
            raise TypeError(
                f"start: {type(self.start)} must equal end:{type(self.end)}"
            )


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start: datetime = datetime.now()
        result = func(*args, **kwargs)
        end: datetime = datetime.now()
        logger.info(f"'{func.__name__}' took {end - start}")

        return result

    return wrapper


def day_count(day: date | None = None) -> int:
    """Returns day of Millenium, relative to input or today"""
    day: date = day or date.today()
    delta: timedelta = day - date(2000, 1, 1)
    return delta.days
