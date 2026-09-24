"""
Define the Atomic Components of the Fields

- NamedField: root

- WriteField: __set__
- OnlyReadField: raise
- ReadField: __get__
- DeleteField: __del__
                                                 DependencyLevel[0]
"""  # FIX: level: bump all or consider _raise as DependencyLevel[-1]?

__all__: list[str] = [
    "NamedField",
    "BaseField",
    "WriteField",
    "OnlyReadField",
    "ReadField",
    "DeleteField",
    "MetaBaseField",
]

from typing import TYPE_CHECKING, Any, Never, Self, overload

from ...port import attach
from ..labor import reflect
from ._raise import FieldRaiser


class NamedField:
    """Provide Utils for all Fields"""

    on_error: type[FieldRaiser] = FieldRaiser

    def __init__(self, *args, **kwargs):
        """Close the chain: super()"""

    def __set_name__(self, owner: type, name: str) -> None:
        _owner = owner
        self.public_name: str = name
        self.private_name: str = f"_{name}"

    def name(self, unit: object) -> str:
        return f"{reflect.clsname(unit)}.{self.public_name}"


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


class WriteField[FieldT](BaseField):
    def __set__(self, unit: object, value: FieldT) -> None:
        self.write(unit, value)

    def write(self, unit: object, value: FieldT) -> None:
        self._set_val(unit, value)


class OnlyReadField(BaseField):
    def __set__(self, unit: object, reject: object) -> Never:
        raise AttributeError(f"{self.name(unit)} is not Writable! {reject=}")


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
            raise self.on_error.ReadMissing(self, unit)()
        return self._get_val(unit)


class DeleteField(BaseField):
    def __delete__(self, unit: object) -> None:
        self.remove(unit)

    def remove(self, unit: object) -> None:
        if self._has_val(unit):
            self._del_val(unit)


class _IdeaFieldAccess(BaseField):
    """Provide a helper Mixin?"""

    @property
    def can_reset(self) -> bool:
        return False

    @property
    def can_load(self) -> bool:  # CHECK: if not redundant
        return False

    def is_readable(self, unit) -> bool:
        return self.can_load or self._has_val(unit)

    def is_writable(self, unit) -> bool:
        return self.can_load or not self._has_val(unit)


class MetaBaseField(NamedField):
    """Bypass mappingproxy to allow Fields to mutate class state"""

    def _get_val(self, unit: type) -> Any:
        return getattr(unit, self.private_name)

    def _set_val(self, unit: type, value: Any) -> None:
        setattr(unit, self.private_name, value)

    def _del_val(self, unit: type) -> None:
        delattr(unit, self.private_name)

    def _has_val(self, unit: type) -> bool:
        return hasattr(unit, self.private_name)


if TYPE_CHECKING:
    _base: type[attach.Descriptor] = NamedField
    _read: type[attach.ReadDescriptor] = ReadField
    _delete: type[attach.WriteDescriptor] = WriteField
    _write: type[attach.DeleteDescriptor] = DeleteField
