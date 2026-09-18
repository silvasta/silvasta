"""
Setup Minimal Components to Assemble individual Descriptors

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "EmitField",
    "ConfigField",
]

from typing import TYPE_CHECKING, Any, NoReturn, TypedDict, Unpack

from ...port.attach import ConfigDescriptor, EventDescriptor
from ...port.event.emit import Emit
from ._base import DeleteField, ReadField, WriteField


class EmitField[T](ReadField[T], WriteField[T], DeleteField):
    def __init__(self, *args, emit: Emit, **kwargs) -> None:
        self.emit: Emit = emit
        super().__init__(*args, **kwargs)

    def write(self, unit: object, value: Any) -> None:
        # LATER: proper Emit binding
        super().write(unit, value)
        # self.emit("on_write", unit=unit, field=self.public_name, value=value)
        raise NotImplementedError

    def remove(self, unit: object) -> None:  # LATER: proper Emit binding
        super().remove(unit)
        # self.emit("on_delete", unit=unit, field=self.public_name)
        raise NotImplementedError


class _ExampleConfig(TypedDict, total=False):
    read_only: bool
    max_length: int | None


class ConfigField(WriteField):
    # REMOVE: _ExampleConfig on first usage, replace by T or dTo
    config = _ExampleConfig(read_only=False, max_length=None)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # IDEA: for later: use config object, more precise  thant this here...
        config_kwargs = {k: v for k, v in kwargs.items() if k in self.config}
        super_kwargs = {
            k: v for k, v in kwargs.items() if k not in self.config
        }
        self.update(**config_kwargs)
        super().__init__(*args, **super_kwargs)

    def update(self, **config: Unpack[_ExampleConfig]):
        # AI: this one is important to update later, or not?
        self.config: _ExampleConfig = {**self.config, **config}

    def check(self, unit, value) -> None | NoReturn:
        # LATER: functor with included checks, Error and Data
        if self.config.get("read_only"):
            raise TypeError(f"{self.public_name} is read-only")

    def write(self, unit: object, value: Any) -> None:
        self.check(unit, value)
        super().write(unit, value)


if TYPE_CHECKING:
    _emit: type[EventDescriptor] = EmitField
    _config: type[ConfigDescriptor] = ConfigField
