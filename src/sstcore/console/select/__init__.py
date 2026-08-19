"""
Launch interactive selectors in TUI or directly from CLI

- selector provides presets

"""

__all__: list = [
    "ListSelectorApp",
    "TreeSelectorApp",
    "selector",
]

from . import _selector as selector
from ._list import ListSelectorApp
from ._tree import TreeSelectorApp
