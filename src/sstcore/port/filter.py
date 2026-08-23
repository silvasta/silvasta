"""
Define the Shape of the Filters

- FilterSpec: Input Space and Data Definition
- Filter: Core Logic

- PathFiltering: Path specification
- ProjectFiltering: Programming Project specification

"""

__all__: list[str] = [
    "Filter",
    "FilterSpec",
    "PathFiltering",
    "ProjectFiltering",
]

from enum import IntEnum, auto
from pathlib import Path
from typing import Protocol, Self, overload

from .error import FailedHackError

# LATER: FilterBox: PathFilter,FileFilter...


class FilterSpec[SetType](Protocol):
    """Define the internal data of the Filter"""

    exclude: set[SetType]
    require_all: set[SetType]
    require_any: set[SetType]

    allow_hidden_files: bool  # NOTE: so far used in ProjectFilter
    return_opposite: bool

    @classmethod
    def from_args(cls, args: FilterSpec[SetType]) -> Self:
        """Build derived class from data containing base"""

    def merge(self, args: Self) -> Self:
        """Update internal Sets with incoming Sets"""

    def subtract(self, args: Self) -> Self:
        """Remove incoming Sets from internal Sets"""


class Filter[SetType, TargetType](FilterSpec, Protocol):
    """Define the matching Rules and how to Call it"""

    def fulfills_exclude(self, target_set: set[SetType]) -> bool:
        """Condition 1: Must NOT have any excluded keywords"""

    def fulfills_require_all(self, target_set: set[SetType]) -> bool:
        """Condition 2: Must have ALL required keywords"""

    def fulfills_require_any(self, target_set: set[SetType]) -> bool:
        """Condition 3: Must have AT LEAST ONE required_any keyword"""

    def fulfills_trio(self, target_set: set[SetType]) -> bool:
        """Check if all 3 conditions are fulfilled (default)"""

    def _fulfill(self, target: TargetType) -> bool:
        """Run validation logic -> override for custom behaviour"""

    @overload
    def __call__(self, target: TargetType) -> bool: ...
    @overload
    def __call__(self, target: list[TargetType]) -> list[TargetType]: ...
    def __call__(
        self, target: TargetType | list[TargetType]
    ) -> bool | list[TargetType]:
        """Check single item (bool) or filter multiple items from list"""


class FilterArgs(IntEnum):
    """Selectable Filter Presets"""

    PROJECT = auto()
    PYTHON = auto()
    RUST = auto()
    LATEX = auto()
    CONFIG = auto()
    DOCS = auto()
    NONE = auto()
    ALL = auto()

    def __call__(self) -> FilterSpec:
        raise FailedHackError("Import sstcore.util.filter to attach args")


class PathFiltering(Filter[str, Path], Protocol):
    """Decomposes Path into parts/stem/suffix for filtering"""


class ProjectFiltering(PathFiltering, Protocol):
    """Filter by Project specific defaults (exclude common dirs, require code files)"""


class FileFiltering(Protocol): ...
