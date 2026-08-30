"""
Provide the Bricks for Descriptor Compositions

-
"""

__all__: list[str] = [
    "NamedField",
    "ReadField",
    "WriteField",
    "DeleteField",
    #
    "ResetField",
    "ValidField",
    "TypedField",
    "EmitField",
    "ConfigField",
]

from typing import (
    TYPE_CHECKING,
    Any,
    NoReturn,
    Self,
    TypedDict,
    Unpack,
    overload,
)

from ...port.attach import (
    ConfigDescriptor,
    DeleteDescriptor,
    EventDescriptor,
    ReadDescriptor,
    Types,
    ValidDescriptor,
    WriteDescriptor,
)
from ...port.event.emit import Emit
from ..format import cls_name, reflect


class NamedField:
    def __init__(self, *args, **kwargs):
        pass

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name: str = name
        self.private_name: str = f"_{name}"

    def _has_val(self, unit: object) -> bool:
        return self.private_name in unit.__dict__

    def _get_val(self, unit: object) -> Any:
        return reflect._dict(unit, key=self.private_name)

    def _set_val(self, unit: object, value: Any) -> None:
        unit.__dict__[self.private_name] = value

    def _del_val(self, unit: object) -> None:
        del unit.__dict__[self.private_name]

    def _cls_attr_name(self, unit: object) -> str:
        """Simply rendered: Cls.attribute"""
        return f"{cls_name(unit)}.{self.public_name}"

    def raise_on_missing(self, unit: object) -> NoReturn:
        raise AttributeError(f"{self._cls_attr_name(unit)} is Missing!")


class ReadField[T](NamedField):
    @overload
    def __get__(self, unit: None, owner: type | None) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type | None) -> T: ...
    def __get__(
        self, unit: object | None, owner: type | None = None
    ) -> T | Self:
        return self if unit is None else self.read(unit)

    def read(self, unit: object) -> T:
        if not self._has_val(unit):
            self.raise_on_missing(unit)
        return self._get_val(unit)


class WriteField[T](NamedField):
    def __set__(self, unit: object, value: T) -> None:
        self.write(unit, value)

    def write(self, unit: object, value: T) -> None:
        self._set_val(unit, value)


class DeleteField(NamedField):
    def __delete__(self, unit: object) -> None:
        self.remove(unit)

    def remove(self, unit: object) -> None:
        if self._has_val(unit):
            self._del_val(unit)


class ResetField[DefaulT](DeleteField):
    def __init__(self, *args, default: DefaulT, **kwargs) -> None:
        self.default: DefaulT = default
        super().__init__(*args, **kwargs)

    def remove(self, unit: object) -> None:
        self._set_val(unit, self.default)


if TYPE_CHECKING:
    _check: type[ReadDescriptor] = ReadDescriptor
    _check: type[WriteDescriptor] = WriteDescriptor
    _check: type[DeleteDescriptor] = DeleteDescriptor


class ValidField[T](WriteField):
    def validate(self, unit: object, value: T) -> T:
        """Finish the loop and return the value"""
        return value

    def write(self, unit: object, value: T) -> None:
        value: T = self.validate(unit, value)
        super().write(unit, value)


class TypedField[T](ValidField[T]):
    def __init__(self, *args, types: Types[T], **kwargs) -> None:
        self.types: Types[T] = types
        super().__init__(*args, **kwargs)

    def raise_on_typing(self, unit: object, value: T) -> T:
        cls_attr: str = self._cls_attr_name(unit)
        raise TypeError(
            f"{cls_attr} expected {self.types!r}, got {cls_name(value)}"
        )

    def validate(self, unit: object, value: T) -> T:
        if not isinstance(value, self.types):
            self.raise_on_typing(unit, value)
        return super().validate(unit, value)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### From here, Experimental
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


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
    _read: type[ReadDescriptor[Any]] = ReadField
    _write: type[WriteDescriptor] = WriteField
    _delete: type[DeleteDescriptor] = DeleteField
    _valid: type[ValidDescriptor] = ValidField
    _emit: type[EventDescriptor] = EmitField
    _config: type[ConfigDescriptor] = ConfigField
