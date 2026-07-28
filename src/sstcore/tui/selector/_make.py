"""
TASK: Collect TuiSelector applications with reusable Pattern

- interface scripts for Textual:
  just throw in any iterable, select, process output, handover
  - check collections from sachmis, flux, robol or others

"""

__all__: list[str] = [
    "multi_linear",
    "single_linear",
]

from loguru import logger

from ...exceptions import TuiSelectorError
from ._list import ListSelectorApp


def multi_linear[T](items: dict[T, str] | list[T] | set[T]) -> list[T]:
    """Select from linear Container and get multiple Elements back"""

    tui = ListSelectorApp(items=items, multi_select=True)

    if selected := tui.run():
        logger.success(f"Selected {len(selected)} elements")
        return selected

    raise TuiSelectorError


def single_linear[T](items: dict[T, str] | list[T] | set[T]) -> T:
    """Select from linear Container and get 1 Element back"""

    tui = ListSelectorApp(items=items, multi_select=False)

    if selected := tui.run():
        item: T = selected[0]
        logger.success(f"Selected: {item=}")
        return item

    raise TuiSelectorError
