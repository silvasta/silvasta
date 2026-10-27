"""
Implement the Mapping and Stacking Pipeline

                        DependencyLevel.sstcore.brick.call.stack[0]
"""

__all__: list[str] = [
    "StackRunner",
    "StackState",
]

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Self

from ....port import stacking
from ....port.link import portlink
from ....port.stacking import LayerMode, RunningStack, StackingLayer
from ....port.stacking import stacking_types as _st


@portlink(RunningStack)
class StackRunner[**In, ValueT, Out]:
    """The transient fluent object that builds state and executes."""

    def __init__(
        self,
        core: stacking.StackingCore[In, ValueT, Out],
        state: stacking.StackingState[ValueT],
    ):
        self._core: stacking.StackingCore[In, ValueT, Out] = core
        # LATER: mixin a core with __call__ and slightly update __getattr__
        self.state: stacking.StackingState[ValueT] = state

    def __getattr__(self, name: str) -> Self:
        if name in self.state.locked_layers:
            raise AttributeError(f"Layer containing '{name}' is locked!")

        if name not in self._core:  # ty:ignore # FIX:
            raise AttributeError(f"'{self._core}' has no attribute '{name}'")

        layer_name: str = self._core.source_map[name]
        layer: StackingLayer[ValueT] = self._core.layers[layer_name]

        if id(value := layer[name]) in self.state.used_value_ids:
            raise AttributeError(f"Value '{name}' already consumed!")

        _new_state = self.state.evolve(layer_name, value, layer.mode)

        return type(self)(self._core, _new_state)

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        return self._core.call(self.state.selected, *args, **kwargs)


@portlink(stacking.StackingState)
@dataclass(frozen=True)
class StackState[T]:
    selected: _st.Accumulated[T] = field(
        default_factory=lambda: defaultdict(list)
    )
    locked_layers: frozenset[str] = frozenset()
    used_value_ids: frozenset[int] = frozenset()

    def evolve(self, layer: str, value: Any, mode: LayerMode) -> Self:
        new_selected: _st.Accumulated[T] = self.selected.copy()
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
