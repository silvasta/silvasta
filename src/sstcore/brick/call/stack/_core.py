"""
Implement the Mapping and Stacking Pipeline

                        DependencyLevel.sstcore.brick.call.stack[1]
"""

__all__: list[str] = [
    "StackCore",
]


from ....port import stacking
from ....port.link import portlink
from ....port.stacking import LayerMode, StackingLayer
from ....port.stacking import stacking_types as _st
from ... import reflect
from ._base import StackLayer
from ._run import StackRunner, StackState


@portlink(stacking.StackingCore)
class StackCore[**In, ValueT, Out](StackLayer[ValueT]):
    def __init__(
        self,
        *layers: StackingLayer[ValueT],
        name: str = "",
        call: stacking.StackApplicator[In, ValueT, Out],
    ):
        name: str = name or str(self)
        self.layers: _st.Map[StackingLayer[ValueT]] = {
            layer.name: layer for layer in layers
        }
        combined_data: _st.LayerData[ValueT] = self.merge_layer()
        super().__init__(combined_data, name, LayerMode.COMBO)
        self.call: stacking.StackApplicator[In, ValueT, Out] = call

    def merge_layer(self) -> _st.LayerData[ValueT]:

        combined_data: _st.LayerData[ValueT] = {}
        self.source_map: _st.Map[str] = {}

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
            layer_name: sorted(layer.keys())
            for layer_name, layer in self.layers.items()
        }

    def __getattr__(self, name: str) -> StackRunner[In, ValueT, Out]:
        if reflect.is_dunder(name):
            raise AttributeError(f"Avoiding dunder: {name}")

        if name not in self:
            raise AttributeError(f"'{self}' has no attribute '{name}'")

        return getattr(StackRunner(self, StackState()), name)
