"""
Provide the Bricks for Descriptor Compositions

-
"""

from sstcore.port.event.emit import Emit

__all__: list[str] = [
    "NamedField",
    "ReadField",
    "WriteField",
    "DeleteField",
    #
    "ValidField",
    "EmitField",
    "ConfigField",
]

from typing import TYPE_CHECKING, Any, Self, TypedDict, Unpack, overload

from ...port.attach import (
    ConfigDescriptor,
    DeleteDescriptor,
    EventDescriptor,
    ReadDescriptor,
    ValidateDescriptor,
    WriteDescriptor,
)


class NamedField:
    public_name: str
    # TODO:
    private_name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name: str = name
        self.private_name: str = f"_{name}"


class ReadField[T](NamedField):
    @overload
    def __get__(self, unit: None, owner: type | None) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type | None) -> T: ...
    def __get__(
        self, unit: object | None, owner: type | None = None
    ) -> T | Self:
        if unit is None:
            return self
        if self.private_name not in unit.__dict__:
            raise AttributeError(f"{self.public_name} is not set")
        # TODO: _read?
        return unit.__dict__[self.private_name]


class WriteField(NamedField):
    def __set__(self, unit: Any, value: Any) -> None:
        # TODO: _write?
        unit.__dict__[self.private_name] = value


class DeleteField(NamedField):
    def __delete__(self, unit: Any) -> None:
        if self.private_name in unit.__dict__:
            del unit.__dict__[self.private_name]


class ResetField(NamedField):
    default: Any

    def __delete__(self, unit: Any) -> None:
        setattr(unit, self.private_name, self.default)


if TYPE_CHECKING:
    _check: type[ReadDescriptor] = ReadDescriptor
    _check: type[WriteDescriptor] = WriteDescriptor
    _check: type[DeleteDescriptor] = DeleteDescriptor


class ValidField(WriteField):
    def validate(self, unit: object, value: Any) -> Any:
        raise NotImplementedError

    def __set__(self, unit: object, value: Any) -> None:
        super().__set__(unit, self.validate(unit, value))


class EmitField(ReadField):
    def __init__(self, func: Emit) -> None:
        self.emit: Emit = func
        raise NotImplementedError


class _ExampleConfig(TypedDict, total=False):
    read_only: bool
    max_length: int | None


class ConfigField(WriteField):
    config = _ExampleConfig(read_only=False, max_length=None)

    def __init__(self, **config: Unpack[_ExampleConfig]) -> None:
        self.update(**config)

    def update(self, **config: Unpack[_ExampleConfig]):
        self.config: _ExampleConfig = {**self.config, **config}

    def __set__(self, unit, value):
        if self.config.get("read_only"):
            raise TypeError(f"{self.public_name} is read-only")
        super().__set__(unit, value)


if TYPE_CHECKING:
    _read: type[ReadDescriptor[Any]] = ReadField
    _write: type[WriteDescriptor] = WriteField
    _delete: type[DeleteDescriptor] = DeleteField
    _valid: type[ValidateDescriptor] = ValidField
    _emit: type[EventDescriptor] = EmitField
    _config: type[ConfigDescriptor] = ConfigField
