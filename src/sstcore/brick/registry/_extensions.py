"""
Extensions for the Core Registry

- FilterRegister
- (FunctorRegistry -> check error.catch._registry for implementation)

"""

__all__: list[str] = [
    "FilterRegistry",
    "FunctorRegistry",  # TODO: check with realisations, e.g. with Handler
]

from typing import TYPE_CHECKING, Any

from ...port.filter import Filter
from ...port.register import FilterRegister


class FunctorRegistry:
    """Same as regular Func registry??"""


class FilterRegistry[FilterT: Filter, ItemT]:
    """Extend the FilterRegistry with filtered items"""

    _active_filter: FilterT | None = None

    def filter(self, new_active_filter: FilterT | None) -> list[ItemT]:
        """Get all files filtered by keywords setup in active_filter"""
        if new_active_filter:
            self.set_filter(new_active_filter)
        return self.active_filter(self._items_to_filter)

    @property
    def _items_to_filter(self) -> list[ItemT]:
        raise NotImplementedError("Missing attribute: _active_filter")

    def set_filter(self, active_filter: FilterT) -> FilterT:
        self._active_filter: FilterT = active_filter
        return self._active_filter

    def reset_filter(self) -> FilterT | None:
        existing: Filter | None = self._active_filter
        self._active_filter = None
        return existing

    @property
    def active_filter(self) -> FilterT:
        """Provide FilterT, bootstrap for non-initialized"""  # LATER: emit?
        if self._active_filter is None:  # LATER: _strict?
            self._active_filter: FilterT = self._load_default_filter()
        return self._active_filter

    def _load_default_filter(self) -> FilterT:
        # LATER: when error location clear, PropertyMissing...Error
        raise NotImplementedError("Missing attribute: _active_filter")


if TYPE_CHECKING:
    _registry: FilterRegister = FilterRegistry()
    _registry: type[FilterRegister[Filter]] = FilterRegistry[Filter, Any]
