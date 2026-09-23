"""
Implement the Mapping and Stacking Pipeline

-
"""

__all__: list[str] = [
    "StackBase",
    "StackLayer",
    "StackCore",
    "StackState",
    "StackRunner",
]

from collections import defaultdict
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, NoReturn, Self

from loguru import logger

from ...port.stacking import (
    Accumulated,
    LayerData,
    LayerMode,
    Map,
    RunningStack,
    StackApplicator,
    StackingCore,
    StackingLayer,
    StackingState,
)
from ..labor import scan


class StackBase[ValueT](Mapping):
    mode: LayerMode
    call: StackApplicator

    def __init__(
        self,
        data: LayerData[ValueT],
        name: str,
    ):
        self.name: str = name
        self._data: LayerData[ValueT] = data

    # LATER: check if this for StackState(Mapping) makes sense
    # def __setitem__(self, key: str, value: ValueT) -> Any:
    #     # IDEA: check here which values are out of order afterwards
    #     # - e.g. for mode.SINGLE: select one, all are closed
    #     # - for mode.MULTI: only 1 is closed, subset remains
    #     raise NotImplementedError(key, value)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.name}]"

    def __repr__(self) -> str:
        return f"{self}[{self.mode}](map={self._data}, call={self.call})"


class StackLayer[ValueT](StackBase[ValueT]):
    def __init__(
        self,
        data: LayerData[ValueT],
        name: str,
        mode: LayerMode = LayerMode.SINGLE,
    ):
        super().__init__(data=data, name=name)
        self.mode: LayerMode = mode

        self._id_to_keys: dict[int, list[str]] = defaultdict(list)
        for k, v in self.items():
            self._id_to_keys[id(v)].append(k)

        self._check_value_duplicates()

    def _check_value_duplicates(self) -> None | NoReturn:
        if len(self._id_to_keys) != len(self):
            message = f"Duplicated values in {self!r}!"
            match self.mode:
                case LayerMode.SINGLE:
                    logger.debug(f"Continue with: {message}")
                case LayerMode.MULTI:
                    raise ValueError(f"Cannot accumulate: {message}")


if TYPE_CHECKING:
    _unit: StackingLayer = StackLayer(data={"blue": "cyan"}, name="color")
    _cls: type[StackingLayer] = StackLayer


class StackCore[**In, ValueT, Out](StackLayer[ValueT]):
    def __init__(
        self,
        *layers: StackingLayer[ValueT],
        name: str = "",
        call: StackApplicator[In, ValueT, Out],
    ):
        name: str = name or str(self)
        self.layers: Map[StackingLayer[ValueT]] = {
            layer.name: layer for layer in layers
        }
        combined_data: LayerData[ValueT] = self.merge_layer()
        super().__init__(combined_data, name, LayerMode.COMBO)
        self.call: StackApplicator[In, ValueT, Out] = call

    def merge_layer(self) -> LayerData[ValueT]:

        combined_data: LayerData[ValueT] = {}
        self.source_map: Map[str] = {}

        for layer in self.layers.values():
            for key, value in layer.items():
                if key in combined_data:
                    message = f"{key!r} in {self.source_map!r} and {layer!r}.."
                    raise KeyError(f"Global Key Collision! {message}")

                combined_data[key] = value
                self.source_map[key] = layer.name

        return combined_data

    def schema(self) -> dict[str, list[str]]:
        return {
            layer_name: list(layer.keys())
            for layer_name, layer in self.layers.items()
        }

    def __getattr__(self, name: str) -> StackRunner[In, ValueT, Out]:
        if scan.is_dunder(name):
            raise AttributeError(f"Avoiding dunder: {name}")

        if name not in self:
            raise AttributeError(f"'{self}' has no attribute '{name}'")

        return getattr(StackRunner(self, StackState()), name)


if TYPE_CHECKING:
    _core: StackingCore = StackCore(call=lambda s: s)
    _cls: type[StackingCore] = StackCore


@dataclass(frozen=True)
class StackState[T]:
    # LATER: think about MappingRegistry with immutable state, maybe on core
    """Immutable accumulation of selected values and masking rules."""

    selected: Accumulated[T] = field(default_factory=lambda: defaultdict(list))
    locked_layers: frozenset[str] = frozenset()
    used_value_ids: frozenset[int] = frozenset()

    def evolve(self, layer: str, value: Any, mode: LayerMode) -> Self:
        new_selected: Accumulated[T] = self.selected.copy()
        new_selected[layer] = new_selected.get(layer, []) + [value]

        new_locked: set[str] = set(self.locked_layers)
        new_used_ids: set[int] = set(self.used_value_ids)

        match mode:
            case LayerMode.SINGLE:
                new_locked.add(layer)
            case LayerMode.MULTI:
                new_used_ids.add(id(value))

        return type(self)(
            selected=new_selected,
            locked_layers=frozenset(new_locked),
            used_value_ids=frozenset(new_used_ids),
        )


if TYPE_CHECKING:
    _state: StackingState = StackState()
    _cls: type[StackingState] = StackState


class StackRunner[**In, ValueT, Out]:
    """The transient fluent object that builds state and executes."""

    def __init__(
        self,
        core: StackingCore[In, ValueT, Out],
        state: StackingState[ValueT],
    ):
        self._core: StackingCore[In, ValueT, Out] = core
        # LATER: mixin a core with __call__ and slightly update __getattr__
        self.state: StackingState[ValueT] = state

    def __getattr__(self, name: str) -> Self:
        if name in self.state.locked_layers:
            raise AttributeError(f"Layer containing '{name}' is locked!")

        if name not in self._core:
            raise AttributeError(f"'{self._core}' has no attribute '{name}'")

        layer_name: str = self._core.source_map[name]
        layer: StackingLayer[ValueT] = self._core.layers[layer_name]

        if id(value := layer[name]) in self.state.used_value_ids:
            raise AttributeError(f"Value '{name}' already consumed!")

        _new_state = self.state.evolve(layer_name, value, layer.mode)

        return type(self)(self._core, _new_state)

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        return self._core.call(self.state.selected, *args, **kwargs)


if TYPE_CHECKING:
    _unit: RunningStack = StackRunner(_core, _state)
    _cls: type[RunningStack] = StackRunner
