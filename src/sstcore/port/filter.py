"""
Define the Shape of the Filters

- FilterSpec: Input Space and Data Definition
- Filter: Core Logic

- PathFiltering: Path specification
- ProjectFiltering: Programming Project specification

"""

__all__: list[str] = [
    "FilterSpec",
    "Filter",
    #
    "FileFiltering",
    "KeyWords",
    "KeyWord",
    #
    "PathFiltering",
    "ProjectFiltering",
    "FilterArgs",
]

from enum import IntEnum, auto
from pathlib import Path
from typing import Protocol, Self, overload

from ..port.files import File
from .error import FailedHackError


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
    def __call__(self, target: list[TargetType]) -> list[TargetType]: ...
    @overload
    def __call__(self, target: TargetType) -> bool: ...
    def __call__(
        self, target: TargetType | list[TargetType]
    ) -> bool | list[TargetType]:
        """Check single item (bool) or filter multiple items from list"""


class FileFiltering[FileT: File](Filter[str, FileT], Protocol):
    def _fulfill(self, target: FileT) -> bool:
        """Filter Registry Files by their Keyword Sets"""


type KeyWords = list[str] | set[str]
type KeyWord = list[str] | set[str] | str
# TASK: generalize for FilterSet, str->hashable, with parameter


class PathFiltering(Filter[str, Path], Protocol):
    def _fulfill(self, target: Path) -> bool:
        """Filter decomposed Paths: parents, name, stem, suffix..."""


class ProjectFiltering(PathFiltering, Protocol):
    def _fulfill(self, target: Path) -> bool:
        """Filter Project by Dir and File Paths"""


class FilterArgs(IntEnum):  # IDEA: FilterData -> FilterInput??
    """Select Presets for Path- and Project Filter"""

    # LATER: FilterBox: provide -> PathFilter,FileFilter...

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
