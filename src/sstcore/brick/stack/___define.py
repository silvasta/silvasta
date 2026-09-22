"""
IMPLEMENT FINAL PROTOCOL HERE

- Temporary until ready to move to proper place

"""

# NEXT: implement

__all__: list[str] = [
    "StackingMap",
    "StackingCore",
]

from collections.abc import Callable, Mapping
from enum import Enum, auto
from typing import Any, Protocol, Self, runtime_checkable

from ...port.calling import Calling

_test: Callable = Calling

type StackOr[T] = T | Callable[[T, Any], T]

type Call[I, S: Mapping, R] = Calling[[I, S], R]

type AttrType[Value] = dict[str, Value]

type AttrRegistry = Mapping[str, tuple[str, Any]]

type StateDict = Mapping[str, Any]

type Mutator[T] = Callable[[T], T]


class LayerMode(Enum):
    """How selections from this layer should be merged."""

    # NEXT: single
    REPLACE = auto()  # Last selection wins
    ACCUMULATE = auto()  # Collect into a tuple (order of selection preserved)
    CUSTOM = auto()  # Use provided merge function


class Applicator[InputT, OutputT](Protocol):
    """Final logic: takes accumulated state + input → result."""

    def __call__(
        self, state: dict[str, Any], value: InputT, context: Any | None = None
    ) -> OutputT: ...


@runtime_checkable
class StackingMap(Protocol):
    """Collect Attributes for 1 Mapping for a Stack"""

    @property
    def mapping(self) -> Mapping: ...


class StackingCore[I, S: Mapping, R](Protocol):
    """The Executing Core"""

    def __getattr__(self, name: str) -> StackingMap:
        """Stack Attributes on top of each other by attribute calls"""

    @property
    def state(self) -> S: ...
    def __call__(self, param=I) -> R: ...

    @classmethod
    def build(
        cls,
        mappings: Mapping[str, Mapping[str, Any]],
        executor: Call[I, S, R],
    ) -> Self: ...


class MaxStackDTO[T]:
    """For Maximal Dispatch on independent Attributes"""

    attr1: str | None = None
    attr2: str | None = None
    attr3: str | None = None

    def __call__(self, arg: Any) -> T:
        """Dipatch by 2^n_attr separate Functions"""

        match self.attr1, self.attr2, self.attr3:
            case None, None, None:
                raise NotImplementedError(arg, self)

            case None, None, _:
                raise NotImplementedError(arg, self)

            case None, _, None:
                raise NotImplementedError(arg, self)

            case None, _, _:
                raise NotImplementedError(arg, self)

            case _, None, None:
                raise NotImplementedError(arg, self)

            case _, None, _:
                raise NotImplementedError(arg, self)

            case _, _, None:
                raise NotImplementedError(arg, self)

            case _, _, _:
                raise NotImplementedError(arg, self)
