"""
Define the Shape of the Stacking Pipeline

-
"""

__all__: list[str] = [
    # define
    "Map",
    "StackData",
    "LayerData",
    "Accumulated",
    "LayerMode",
    # stack
    "StackingLayer",
    "StackingCore",
    "StackApplicator",
    "StackingState",
    "RunningStack",
]

from collections.abc import Callable, Mapping
from enum import Enum, auto
from typing import Any, Protocol, Self, runtime_checkable

type Map[T] = Mapping[str, T]
type StackData[T] = T | Callable[..., T]
type LayerData[T] = Map[StackData[T]]

type Accumulated[T] = dict[str, list[T]]


class LayerMode(Enum):
    """Govern StackLayer Behaviour"""

    SINGLE = auto()
    MULTI = auto()
    COMBO = auto()


class StackingLayer[T](Protocol):
    """Collect Attributes for 1 Mapping for a Stack"""

    @property
    def name(self) -> str: ...
    @property
    def mode(self) -> LayerMode: ...

    def __contains__(self, target: T, /) -> bool: ...  # LATER: use registry
    def __getitem__(self, key: str) -> T: ...  # LATER: use registry


class StackingCore[**I, T, R](StackingLayer, Protocol):
    """The Executing Core - Connect Layers and Runtime State"""

    @property
    def layers(self) -> Map[StackingLayer]:  # LATER: field
        """Store Mapping with Source Layer"""

    @property
    def source_map(self) -> Map[str]:  # LATER: field
        """Store Mapping linking Attributes back to Source Layer"""

    @property
    def call(self) -> StackApplicator[I, T, R]:  # LATER: field
        """Collect and Provide Application Funcion"""

    def __getattr__(self, name: str) -> RunningStack:
        """Launch Initial State for repeated Access"""


@runtime_checkable
class StackApplicator[**In, T, Out](Protocol):
    def __call__(
        self, state: Accumulated[T], *args: In.args, **kwargs: In.kwargs
    ) -> Out:
        """Generate Result from collected Stacks applied to Input"""


class StackingState[**I, T, R](Protocol):
    """Rebuild Immutable State on every hop"""

    @property
    def selected(self) -> dict[str, list[T]]: ...
    @property
    def locked_layers(self) -> frozenset[str]: ...
    @property
    def used_value_ids(self) -> frozenset[int]: ...

    def evolve(self, layer: str, value: Any, mode: LayerMode) -> Self:
        """Create new State with updated Constraints"""


class RunningStack[**I, T, R](Protocol):
    """The Running Engine - Update State while hopping forward"""

    @property
    def state(self) -> StackingState: ...
    def __call__(self, *args: I.args, **kwargs: I.kwargs) -> R: ...
    def __getattr__(self, name: str) -> Self:
        """Stack Attributes by Dot-Access"""
