"""
Define the Atomic Components of the Fields

- NamedField: root

- WriteField: __set__
- NoWriteField: raise
- ReadField: __get__
- DeleteField: __del__
                                                 DependencyLevel[1]
"""

__all__: list[str] = [
    "NamedField",
    "BaseField",
    "WriteField",
    "NoWriteField",
    "ReadField",
    "DeleteField",
]

from typing import Any, Never, Self, overload

from ...port import attach
from ...port.link import portlink
from ..labor import reflect
from ._raise import FieldRaiser


@portlink(attach.Descriptor)
class NamedField:
    """Provide Name for all Fields"""

    raiser: type[FieldRaiser] = FieldRaiser

    def __init__(self, *args, **kwargs):
        """Close the chain: super()"""

    def __set_name__(self, owner: type, name: str) -> None:
        _owner = owner
        self.public_name: str = name
        self.private_name: str = f"_{name}"

    def name(self, unit: object) -> str:
        return f"{reflect.clsname(unit)}.{self.public_name}"


@portlink(attach.Descriptor)
class BaseField(NamedField):
    """Provide Utils for all Fields"""

    def _get_val(self, unit: object) -> Any:
        return unit.__dict__[self.private_name]

    def _set_val(self, unit: object, value: Any) -> None:
        unit.__dict__[self.private_name] = value

    def _del_val(self, unit: object) -> None:
        del unit.__dict__[self.private_name]

    def _has_val(self, unit: object) -> bool:
        return self.private_name in unit.__dict__


@portlink(attach.WriteDescriptor)
class WriteField[FieldT](BaseField):
    def __set__(self, unit: object, value: FieldT) -> None:
        self.write(unit, value)

    def write(self, unit: object, value: FieldT) -> None:
        self._set_val(unit, value)


class NoWriteField(BaseField):
    def __set__(self, unit: object, reject: object) -> Never:
        raise self.raiser.ReadOnly(
            self, unit, attr=self.public_name, value=reject
        )


@portlink(attach.ReadDescriptor)
class ReadField[FieldT](BaseField):
    @overload
    def __get__(self, unit: None, owner: type | None) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type | None) -> FieldT: ...
    def __get__(
        self, unit: object | None, _owner: type | None = None
    ) -> FieldT | Self:
        """Dispatch by Caller: unit=instance or owner=type(instance)"""

        return self if unit is None else self.read(unit)

    def read(self, unit: object) -> FieldT:
        if not self._has_val(unit):
            raise self.raiser.ReadMissing(self, unit)
        return self._get_val(unit)


@portlink(attach.DeleteDescriptor)
class DeleteField(BaseField):
    def __delete__(self, unit: object) -> None:
        self.remove(unit)

    def remove(self, unit: object) -> None:
        if self._has_val(unit):
            self._del_val(unit)
