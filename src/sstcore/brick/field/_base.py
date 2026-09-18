"""
Define the Atomic Components of the Fields

- NamedField: root

- ReadField: __get__
- WriteField: __set__
- DeleteField: __del__
                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "NamedField",
    "ReadField",
    "WriteField",
    "DeleteField",
    "OnlyReadField",
    "FieldDecorator",
]

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Never, Self, overload

from ...port import attach
from ..labor import reflect


class NamedField:
    """Provide Utils for all Fields"""

    def __init__(self, *args, **kwargs):
        """Close super()"""

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name: str = name
        self.private_name: str = f"_{name}"

    def name(self, unit: object) -> str:
        return f"{reflect.clsname(unit)}.{self.public_name}"

    def _get_val(self, unit: object) -> Any:
        return reflect._dict(unit, key=self.private_name)

    def _set_val(self, unit: object, value: Any) -> None:
        unit.__dict__[self.private_name] = value

    def _del_val(self, unit: object) -> None:
        del unit.__dict__[self.private_name]

    def _has_val(self, unit: object) -> bool:
        return self.private_name in unit.__dict__


class ReadField[T](NamedField):
    @overload
    def __get__(self, unit: None, owner: type | None) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type | None) -> T: ...
    def __get__(
        self, unit: object | None, owner: type | None = None
    ) -> T | Self:
        return self if unit is None else self.read(unit)

    def raise_on_missing(self, unit: object) -> Never:
        raise AttributeError(f"{self.name(unit)} is Missing!")

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


class OnlyReadField(NamedField):
    def __set__(self, unit: object, value: object) -> None:
        raise AttributeError(f"{self.name(unit)} Path is not Writable!")


# NEXT:
class FieldDecorator(NamedField):  # TODO: Parametrization
    def __init__(  # IDEA: use Calling?
        self, target: Callable | None = None, *args: Any, **kwargs: Any
    ) -> None:
        """Check if Decorator has Input -> Bind or Attach"""

        # TODO: better intermediate storage somehow?
        self.target_input: Callable | None = target

        if target is not None:
            self._bind_func(target)

        super().__init__(*args, **kwargs)

    def __call__(self, target_func: Callable) -> Self:
        """Invoked only when used as @Field(args)"""
        self.target_func = target_func
        self._bind_func(target_func)
        return self

    def _bind_func(self, target_func: Callable) -> None:  # LATER: rename: bind
        self.__doc__: str | None = target_func.__doc__  # EXTRACT: for reflect
        # WARN: check super() for public_name consistency
        self.public_name: str = reflect.dig.func(target_func)  # TODO: default?


if TYPE_CHECKING:
    _base: type[attach.DescriptorBase] = NamedField
    _read: type[attach.ReadDescriptor] = ReadField
    _delete: type[attach.WriteDescriptor] = WriteField
    _write: type[attach.DeleteDescriptor] = DeleteField
    _deco: type[attach.DecoratingField] = FieldDecorator
