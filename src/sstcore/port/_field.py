from typing import Self, overload

from .attach import Types


class FixTypeField[FieldT]:
    def __init__(self, types: Types[FieldT]) -> None:
        self._types: Types[FieldT] = types

    def name(self, unit: object) -> str:
        return f"{type(unit).__name__}.{self.public_name}"

    def __set_name__(self, _owner: type, name: str) -> None:
        self.public_name: str = name
        self.private_name: str = f"_{name}"

    def __set__(self, unit: object, value: FieldT) -> None:
        if self.private_name in unit.__dict__:  # TODO: raiser
            raise AttributeError(
                f"{self.name(unit)} is frozen and cannot be reassigned!"
            )
        if not isinstance(value, self._types):  # TODO: raiser
            raise TypeError(
                f"Validation failed for {self.name(unit)}. "
                f"Expected {self._types}, got {type(value).__name__}."
            )
        unit.__dict__[self.private_name] = value

    @overload
    def __get__(self, unit: None, _owner: type | None = None) -> Self: ...

    @overload
    def __get__(self, unit: object, _owner: type | None = None) -> FieldT: ...
    def __get__(self, unit: object | None, _owner=None) -> FieldT | Self:
        if unit is None:
            return self
        if self.private_name not in unit.__dict__:  # TODO: raiser
            raise AttributeError(f"{self.name(unit)} is Missing! {self}")
        return unit.__dict__[self.private_name]
