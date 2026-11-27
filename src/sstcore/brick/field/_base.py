"""
Define the Atomic Components of the Fields

- NamedField: root

- WriteField: __set__
- ReadOnlyField: raise
- ReadField: __get__
- DeleteField: __del__
                                                 DependencyLevel[1]
"""

__all__: list[str] = [
    "NamedField",
    "BaseField",
    "WriteField",
    "ReadOnlyField",
    "ReadField",
    "DeleteField",
]

from typing import Any, Never, Self, overload

from ...port import attach
from ...port.empty import VOID, MayNot
from ...port.link import portlink
from ...port.primitives import Kwargs
from .. import reflect
from ._raise import FieldRaiser


@portlink(attach.Descriptor)
class NamedField:
    """Provide Name for all Fields"""

    raiser: type[FieldRaiser] = FieldRaiser

    def __init__(self, *args, **kwargs):
        """Close the chain: super()"""

    def __set_name__(self, owner: type, name: str) -> None:
        _ = owner
        self.public_name: str = name
        self.private_name: str = f"_{name}"

    def __repr__(self) -> str:  # LATER: use __format__ for multiline
        return f"{self}[\n{Kwargs.vars(self):nv}\n]"

    def __str__(self) -> str:
        name: str = getattr(self, "public_name", "FIELD")
        return f"{reflect.clsname(self)}.{name}"


class _SlotBaseField(NamedField):
    # TASK: wire this
    # - use mode:Literal["dict","slots"]
    # - maybe runtime toggle?
    def __init__(
        self, *args, default: Any = VOID, frozen: bool = False, **kwargs
    ):
        self.default: Any = default
        self.frozen: bool = frozen
        super().__init__(*args, **kwargs)

    def _get_val(self, unit: object) -> Any:
        return object.__getattribute__(unit, self.private_name)

    def _set_val(self, unit: object, value: Any) -> None:
        object.__setattr__(unit, self.private_name, value)

    def _del_val(self, unit: object) -> None:
        object.__delattr__(unit, self.private_name)

    def _has_val(self, unit: object) -> bool:
        try:
            object.__getattribute__(unit, self.private_name)
            return True
        except AttributeError:
            return False


@portlink(attach.Descriptor)
class BaseField(NamedField):
    """Provide Utils for all Fields"""

    def __init__(
        self, *args, default: Any = VOID, frozen: bool = False, **kwargs
    ):
        self.default: Any = default
        self.frozen: bool = frozen
        super().__init__(*args, **kwargs)

    def _get_val(self, unit: object) -> Any:
        return unit.__dict__[self.private_name]

    def _set_val(self, unit: object, value: Any) -> None:
        # TODO: frozen? or this as escape of frozen?
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
        if self.frozen and self._has_val(unit):
            raise self.raiser.ReadOnly(self, unit)
        self._set_val(unit, value)


class ReadOnlyField(BaseField):  # IDEA: block read and delete field?
    def __set__(self, unit: object, value: Never) -> Never:
        raise self.raiser.ReadOnly(self, unit, value=value)

    def __delete__(self, unit: object) -> Never:
        raise self.raiser.ReadOnly(self, unit, attr=self.public_name)


@portlink(attach.ReadDescriptor)
class ReadField[FieldT](BaseField):
    @overload
    def __get__(self, unit: None, owner: type | None) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type | None) -> FieldT: ...
    # AI_QUESTION: is owner ever None? should always be a Cls right?
    def __get__(
        self, unit: MayNot[object], owner: type | None = None
    ) -> FieldT | Self:
        """Dispatch by Caller: unit=instance or owner=type(instance)"""
        _ = owner
        return self if unit is None else self.read(unit)

    def read(self, unit: object) -> FieldT:
        if not self._has_val(unit):
            if self.default is not VOID:
                return self.default
            raise self.raiser.ReadMissing(self, unit)
        return self._get_val(unit)


@portlink(attach.DeleteDescriptor)
class DeleteField(BaseField):
    def __delete__(self, unit: object) -> None:
        self.remove(unit)

    def remove(self, unit: object) -> None:
        if self._has_val(unit):
            self._del_val(unit)
