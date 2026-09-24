"""
Define the Shape of the Stacking Pipeline

- Repeated Dot-Access on Callables to stack Modifications

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

# LATER: make all imports _private
from collections.abc import (
    Callable,
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    ValuesView,
)
from enum import Enum, auto
from typing import Any, Protocol, Self, runtime_checkable

type Map[ValueT] = Mapping[str, ValueT]
type StackData[ValueT] = ValueT | Callable[..., ValueT]
type LayerData[ValueT] = Map[StackData[ValueT]]

type Accumulated[ValueT] = dict[str, list[ValueT]]


def test() -> Map:
    raise NotImplementedError


class LayerMode(Enum):
    """Govern StackLayer Behaviour"""

    SINGLE = auto()
    MULTI = auto()
    COMBO = auto()


class StackingLayer[ValueT](Protocol):
    """Collect Attributes for 1 Mapping for a Stack"""

    @property
    def name(self) -> str: ...
    @property
    def mode(self) -> LayerMode: ...

    def __contains__(self, target: ValueT, /) -> bool: ...
    def __getitem__(self, key: str) -> ValueT: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[str]: ...
    def keys(self) -> KeysView[str]: ...
    def values(self) -> ValuesView[ValueT]: ...
    def items(self) -> ItemsView[str, ValueT]: ...


class StackingCore[**In, ValueT, Out](StackingLayer[ValueT], Protocol):
    """The Executing Core - Connect Layers and Runtime State"""

    @property
    def layers(self) -> Map[StackingLayer[ValueT]]:  # LATER: field
        """Store Mapping with Source Layer"""

    def schema(self) -> dict[str, list[str]]:
        """Generate Layer Mapping as SSoT for Stub typing"""

    @property
    def source_map(self) -> Map[str]:  # LATER: field
        """Store Mapping linking Attributes back to Source Layer"""

    @property
    def call(self) -> StackApplicator[In, ValueT, Out]:  # LATER: field
        """Collect and Provide Application Funcion"""

    def merge_layer(self) -> LayerData[ValueT]:
        """Combine multiple StackLayer to Mapping for StackCore"""

    def __getattr__(self, name: str) -> RunningStack:
        """Launch Initial State for repeated Access"""


@runtime_checkable
class StackApplicator[**In, ValueT, Out](Protocol):
    def __call__(
        self, state: Accumulated[ValueT], *args: In.args, **kwargs: In.kwargs
    ) -> Out:
        """Generate Result from collected Stacks applied to Input"""


class StackingState[ValueT](Protocol):
    """Rebuild Immutable State on every hop"""

    @property
    def selected(self) -> dict[str, list[ValueT]]: ...
    @property
    def locked_layers(self) -> frozenset[str]: ...
    @property
    def used_value_ids(self) -> frozenset[int]: ...

    def evolve(self, layer: str, value: Any, mode: LayerMode) -> Self:
        """Create new State with updated Constraints"""


class RunningStack[**In, ValueT, Out](Protocol):
    """The Running Engine - Update State while hopping forward"""

    @property
    def state(self) -> StackingState[ValueT]: ...
    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out: ...
    def __getattr__(self, name: str) -> Self:
        """Stack Attributes by Dot-Access"""
