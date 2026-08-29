"""
Class attribute Fields

- Attach with Descriptor
"""

__all__: list[str] = [
    "Injected",
    "Collected",
    "Derived",
    "Format",
]

from typing import TYPE_CHECKING, Any, Self, overload

from ...port.attach import (
    FieldLoader,
    LazyDescriptor,
    ReadDescriptor,
    ValidateDescriptor,
    WriteDescriptor,
)
from ..format import reflect
from ._base import ReadField, ValidField

type Types[T] = type[T] | tuple[type[T], ...]


class Injected[T](ReadField, ValidField):
    """Required instance attribute. No default. Set before first get."""

    def __init__(self, expected: Types[T] | None = None) -> None:
        self.expected: Types[T] | None = expected

    def validate(self, unit: object, value: T) -> T:
        if self.expected and not isinstance(value, self.expected):
            raise TypeError(
                f"{reflect.cls_name(unit)}.{self.public_name} expected "
                f"{self.expected!r}, got {reflect.cls_name(value)}"
            )
        return value


class Collected[T](ReadField[T]):
    """Lazy cached value. Factory runs once per instance on first get."""

    def __init__(self, loader: FieldLoader) -> None:
        self.loader: FieldLoader = loader

    @overload
    def __get__(self, unit: None, owner: type | None) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type | None) -> T: ...
    def __get__(
        self, unit: object | None, owner: type | None = None
    ) -> T | Self:

        if unit and self.private_name not in unit.__dict__:
            self.__set__(unit, self.loader(unit))

        return super().__get__(unit, owner)

    def __set__(self, unit: object, value: T) -> None:
        unit.__dict__[self.private_name] = value


class Derived[T](ReadField[T]):
    """Computed view. No storage, no setter — subclasses may replace the descriptor."""

    def __init__(self, func: FieldLoader) -> None:
        """Named Method"""
        self.func: FieldLoader = func
        self.__doc__: str | None = func.__doc__
        self.public_name: str = reflect.func(func)

    @overload
    def __get__(self, unit: None, owner: type | None) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type | None) -> T: ...
    def __get__(
        self, unit: object | None, owner: type | None = None
    ) -> T | Self:
        return self if unit is None else self.func(unit)


class Forward(ReadField):
    """A descriptor that forwards method calls to an inner attribute."""

    def __init__(self, target_attr, method_name):
        self.target_attr = target_attr
        self.method_name = method_name

    def __get__(self, unit: object | None, owner: type | None = None) -> Any:
        if unit is None:
            return self
        target = getattr(unit, self.target_attr)
        return getattr(target, self.method_name)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Specifications
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Format(Derived[str]):
    def __init__(self, template: str) -> None:
        super().__init__(lambda unit, t=template: t.format(info=unit.info))


class RegistryField(Collected):  # NEXT:
    """Attach Container to SstRegistry"""


if TYPE_CHECKING:
    _injected: type[WriteDescriptor] = Injected
    _injected: type[ValidateDescriptor] = Injected
    _collected: type[LazyDescriptor[Any]] = Collected
    _derived: type[ReadDescriptor[Any]] = Derived
