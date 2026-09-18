"""
Govern the Shape and Structure of the Strict and Reliable Container

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "EnumZero",
    "Identifier",
]


from enum import Enum
from typing import Self, Any, TypedDict, NamedTuple, Unpack, Never

# IDEAS: module name
# - strict
# - reliable
# - relying
# - define
# - govern

# STRATEGY: - General Setup
# - evaluate on int|str|self
# - str: name.lower() or shortcut

# STRATEGY: - Axis: Implementation 1
# - Grid:
#  - ColorGrid
#  - registry?
# - int: range 0..n

# STRATEGY: - Option: Implementation 2
# - Policy:
#   - PolicyDescriptor
#   - Machine
# - Select:
#   - PrintOption
# - int: default on 0

# STRATEGY: - Catalog: Implementation 3
# - Mixin
# - FuncExecute
# - int: 1 or slice[1...N] or even 0 for no select

# NEXT: Transission? State? Graph?

# TASK: base enum to derive
# - __str__
# - __repr__
# - index
# __getitem__


# LATER:
# ERROR: meta modified base enum


# LATER: SstEnum - from scratch

# IDEA: EnumRaiser: raise_on.X
# def raise_on_unbound(self, unit: object) -> Never:
#     raise RuntimeError(f"{self.name(unit)} Missing Function!")
# def raise_on_signature(self, unit: object, bad_func: Any) -> Never:
#     message: str = (
#         f"{self.name(unit)} expected {self.signature!r}, got {bad_func}"
#         if self.signature is not None
#         else f"{self.name(unit)} Missing Signature! Call: {bad_func=}"  )
#     raise TypeError(message)


class EnumStr1(Enum):
    def __str__(self) -> str:
        return f"{self.name.capitalize()}"


class EnumStr2(Enum):
    def __str__(self):
        return self.name


class EnumRepr1(Enum):
    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.value}]::{self}"


type Identifier[EnumT] = EnumT | str | int


class EnumZero(Enum):
    """Define enumerated Axis for {0..N} members"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> int:
        """Return the index of the Color inside the Palette"""
        return count

    def resolve(
        self, guess: Identifier[Self], default: Self | None = None
    ) -> Self:
        """Map [int|str|EnumT] to EnumT, Default or Raise"""
        enum = type(self)
        try:
            match guess:
                case enum():
                    return guess

                case int() as index:
                    return enum(index)

                case str() as name:
                    return enum[name.upper()]

                case _:
                    raise ValueError(f"Unrecognized type: {type(guess)}")

        except (ValueError, KeyError) as error:
            if default is None:
                raise ValueError(f"Mapping {enum} failed: {guess=}") from error
        return default


class ErrorInput(TypedDict, total=False):
    """Define the Kwarg Space of the Error Pipeline"""


class ErrorData[FieldT, UnitT](NamedTuple):
    """Define the Arg Space of the Internal Pipeline"""

    raiser: str
    #
    # field: FieldT
    # instance: UnitT | None = None
    # cls_attr_name: str = ""  # Cls.attr
    #
    # owner: type | None = None
    # value: FieldT | Any = None
    #
    expected: tuple[tuple[str, Any], ...] = ()
    received: tuple[tuple[str, Any], ...] = ()
    #
    extra: dict[str, Any] | None = None  # CHECK: can here something change?


class ErrorDTO[ErrorT: Exception](NamedTuple):
    """Define the Boundary of the Outgoing Message"""

    error: type[ErrorT]
    message: str = ""
    args: tuple[Any, ...] = ()

    def __call__(self, *args) -> ErrorT:
        return self.error(self.message, *self.args, *args)

    def fire(self, *args) -> Never:
        raise self(self.message, *self.args, *args)


class Raiser(EnumZero, EnumRepr1, EnumStr2):
    def __call__(self, **kwargs: Unpack[ErrorInput]) -> Never:
        """Collect the needed input, format and fire the Exception"""

        def _sanitize(**kwargs: Unpack[ErrorInput]) -> ErrorInput:
            raise NotImplementedError

        input_dto: ErrorInput = _sanitize(**kwargs)
        output_dto: ErrorDTO = ErrorBuilder()(self, input_dto)

        self.launch(output_dto)

    def launch(self, data: ErrorDTO, *args) -> Never:
        raise data.fire(data.message, *data.args, *args)
