"""
Assemble Class Based Descriptors

- EXPERIMENTAL
                                                 DependencyLevel[x]
"""

from enum import Enum

__all__: list[str] = [
    "MetaStateField",
    "MetaBaseField",
    "MetaReadField",
    "MetaWriteField",
    "MetaValidField",
    "MetaTypedField",
]

from typing import Any, Never, Self

from ....port.attach import Types
from ...labor import clsname


class _NamedFieldCopy:
    """Provide Utils for all Fields"""

    def __init__(self, *args, **kwargs):
        """Close the chain: super()"""

    def __set_name__(self, owner: type, name: str) -> None:
        _owner = owner
        self.public_name: str = name
        self.private_name: str = f"_{name}"

    def name(self, unit: object) -> str:
        return f"{clsname(unit)}.{self.public_name}"


class MetaBaseField(_NamedFieldCopy):
    """Bypass mappingproxy to allow Fields to mutate class state"""

    def _get_val(self, unit: type) -> Any:
        return getattr(unit, self.private_name)

    def _set_val(self, unit: type, value: Any) -> None:
        setattr(unit, self.private_name, value)

    def _del_val(self, unit: type) -> None:
        delattr(unit, self.private_name)

    def _has_val(self, unit: type) -> bool:
        return hasattr(unit, self.private_name)


class MetaReadField[FieldT](MetaBaseField):
    def __get__(
        self, unit: type | None, _owner: type | None = None
    ) -> FieldT | Self:
        """Dispatch by Caller: unit=instance or owner=type(instance)"""

        return self if unit is None else self.read(unit)

    def on_erroron_missing(self, unit: object) -> Never:
        # REMOVE: when on_error established
        raise AttributeError(f"{self.name(unit)} is Missing!")

    def read(self, unit: type) -> FieldT:
        if not self._has_val(unit):
            self.on_erroron_missing(unit)
        return self._get_val(unit)


class MetaWriteField[FieldT](MetaBaseField):
    def __set__(self, unit: type, value: FieldT) -> None:
        self.write(unit, value)

    def write(self, unit: type, value: FieldT) -> None:
        self._set_val(unit, value)


class MetaValidField[FieldT](MetaWriteField):
    def validate(self, unit: type, value: FieldT) -> FieldT:
        """Finish the loop and return the value"""
        return value

    def write(self, unit: type, value: FieldT) -> None:
        value: FieldT = self.validate(unit, value)
        super().write(unit, value)


class MetaTypedField[FieldT](MetaValidField[FieldT]):
    def __init__(self, *args, types: Types[FieldT], **kwargs) -> None:
        self.types: Types[FieldT] = types
        super().__init__(*args, **kwargs)

    def raise_on_typing(self, unit: object, value: FieldT) -> Never:
        _m = f"{self.name(unit)} expected {self.types!r}, got {clsname(value)}"
        raise TypeError(_m)

    def validate(self, unit: type, value: FieldT) -> FieldT:
        if not isinstance(value, self.types):
            self.raise_on_typing(unit, value)
        return super().validate(unit, value)


class MetaStateField[T: Enum](MetaTypedField[T], MetaReadField[T]):
    """State graph evaluation for class-level namespaces"""
