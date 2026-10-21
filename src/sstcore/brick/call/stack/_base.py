"""
Implement the Mapping and Stacking Pipeline

                        DependencyLevel.sstcore.brick.call.stack[0]
"""

__all__: list[str] = [
    "StackBase",
    "StackLayer",
]

from collections import defaultdict
from collections.abc import Iterator, Mapping
from typing import Any, NoReturn

from loguru import logger

from ....port import stacking
from ....port.link import portlink
from ....port.stacking import LayerMode, StackingLayer
from ....port.stacking import stacking_types as _st


class StackBase[ValueT](Mapping):
    mode: LayerMode
    call: stacking.StackApplicator

    def __init__(
        self,
        data: _st.LayerData[ValueT],
        name: str,
    ):
        self.name: str = name
        self._data: _st.LayerData[ValueT] = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, value) -> bool:
        return value in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.name}]"

    def __repr__(self) -> str:
        return f"{self}[{self.mode}](map={self._data}, call={self.call})"


@portlink(StackingLayer)
class StackLayer[ValueT](StackBase[ValueT]):
    def __init__(
        self,
        data: _st.LayerData[ValueT],
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
