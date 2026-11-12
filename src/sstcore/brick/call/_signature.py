"""
Analyze the Signature of Callables

-
"""

__all__: list[str] = [
    "Param",
    "ArgTuple",
    "ArgKind",
    "SigParam",
]

from collections.abc import Iterator
from dataclasses import dataclass
from enum import auto
from inspect import Parameter, Signature, _empty, _ParameterKind
from typing import Any, NamedTuple, Self, overload, reveal_type

from ...port.solid import EnumZero

EMPTY: type[_empty] = _empty

s = Signature()
p = Parameter("name", _ParameterKind.KEYWORD_ONLY)

reveal_type(p.annotation)


class Param(EnumZero):  # IDEA: SigParam, Sig, SigPart, SigKind
    """
    Govern the 5 Parameter Kinds - f(a, /, b, b=B, *c, d=D, **e)

    - 0: Pure Positional Arguments
    - 1: Mixed Positional and Keyword Arguments
    - 2: Unbound Tuple(len[0,..N]) with Positional Arguments
    - 3: Pure Keyword Arguments
    - 4: Unbound Dict(len[0,..N]) with Keyword Arguments

    """

    POSARG = auto()
    ANYARG = auto()
    ARGS = auto()
    KEYARG = auto()
    KWARGS = auto()
    # IDEA: RETURN

    def to_inspect(self) -> _ParameterKind:
        """Provide corresponding inspect._ParameterKind"""
        return _ParameterKind(self.value)

    @overload
    @classmethod
    def map(cls, target: Param, /) -> _ParameterKind: ...
    @overload
    @classmethod
    def map(cls, target: _ParameterKind, /) -> Param: ...
    @classmethod
    def map(cls, target: Param | _ParameterKind, /) -> _ParameterKind | Param:
        """Swap sstcore.Param or inspect._ParameterKind to counterpart"""
        match target:
            # CHECK: RETURN, no counterpart
            case Param():
                return _ParameterKind(target.value)
            case _ParameterKind():
                return Param(target.value)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ArgTuple(NamedTuple):
    """Define the Spec of 1 Signature Parameter"""

    name: str
    kind: Param
    default: Any = Any
    annotation: Any = Any

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.name}]::{self.kind}"

    # def __contains__(self, value) -> bool:
    #     """Maybe"""


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ArgKind[Kind: Param]:
    """Define the Rules for 1 Signature Parameter Kind"""

    __slots__ = ("_data",)

    def __init__(self, *args: ArgTuple):
        self._data: dict[ArgTuple, None] = {arg: None for arg in args}

    @property
    def names(self) -> list[str]:
        return [arg.name for arg in self._data]

    @property
    def kinds(self) -> list[Kind]:  # TODO: just return 1 enum value
        # AI: how to make a proper test?
        kinds: list[Kind] = []
        for arg in self._data:
            if not isinstance(arg.kind, Kind):
                raise
            else:
                kinds.append(arg.kind)
        return kinds

    def __str__(self) -> str:
        return f"{type(self).__name__}[{','.join(self.names)}]"

    def __repr__(self) -> str:
        return f"{self}({','.join(f'{arg!r}' for arg in self)})"

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[ArgTuple]:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        # TODO:
        # - check by name
        # - check by ArgTuple
        # - what else?
        # return item in self._data
        raise NotImplementedError(item)

    def __getitem__(self, key: str) -> Any:
        # TODO:
        # - get by name?
        # return self._data[key]
        raise NotImplementedError(key)

    # TODO: ??
    # def __setitem__(self, key: str) -> Any:

    def __sub__(self, other: Self) -> Self:
        # CHECK:
        if not isinstance(other, type(self)):
            return NotImplemented
        _new_args = (arg for arg in self._data if arg not in other._data)
        return type(self)(*_new_args)

    def __and__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        _new_args = (arg for arg in self._data if arg in other._data)
        return type(self)(*_new_args)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

# STRATEGY: define rules per category, IF needed
# - may be possible to apply the rules in the main Sig class
# - *args and **kwargs may collapse
# - check what is required or useful, implement tiny helper or combine
# - use mixins if it reduces combinatorial issues


class PosArgs(ArgKind): ...


class AnyArgs(ArgKind): ...


class Args(ArgKind): ...


class KeyArgs(ArgKind): ...


class Kwargs(ArgKind): ...


#  LINE: -- Return -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#
def get_return(target: type):
    """
        Just as info how it works

        for -> Any the __annotations__ contain "return":typing.Any
        - Any and EMPTY cannot be used with is{instance|subclass}
    In lenient mode, empty is implicitly treated as Any.

    In strict mode (e.g., mypy --disallow-untyped-defs), empty is an error—it
    """
    if "return" not in target.__annotations__:
        _result = EMPTY


#  LINE: -- Signature -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class SigParam:
    pos: PosArgs
    both: AnyArgs
    args: Args
    key: KeyArgs
    kwargs: Kwargs

    result: Any

    def __sub__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        # Delegates the difference logic to the individual groups
        # return type(self)(
        #     speed_data=self.speed_data - other.speed_data,
        #     temp_data=self.temp_data - other.temp_data,
        # )
        raise NotImplementedError

    def __and__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        # Delegates the intersection logic to the individual groups
        # return MainContainer(
        #     speed_data=self.speed_data & other.speed_data,
        #     temp_data=self.temp_data & other.temp_data,
        # )
        raise NotImplementedError


if __name__ == "__main__":
    from rich import print

    for member in _ParameterKind:
        print(f"{member.name:<21} -> {Param.map(member)=}")

    for member in Param:
        print(f"{member.name:<9} -> {Param.map(member)=}")

    inspect_kwarg: _ParameterKind = Parameter.VAR_POSITIONAL
    sigcast_kwarg: Param = Param.KWARGS

    x: Param = Param.map(inspect_kwarg)
    y: _ParameterKind = Param.map(sigcast_kwarg)

    arg1 = ArgTuple("test", Param.ANYARG)
    arg2 = ArgTuple("other", Param.KWARGS)

    print(arg1)
    print(arg2)
    print(f"str: {arg2} repr: {arg2=}")

    print(f"{"test" in arg1=}")
    print(f"{"fail" in arg1=}")
    print(f"{Any in arg1=}")

    mapping1 = ArgKind()
    mapping2 = ArgKind(arg1, arg2)

    print(mapping1)
    print(mapping2)
    print(f"str: {mapping2} repr: {mapping2=}")
    print(f"{mapping1} is: {bool(mapping1)}")
    print(f"{mapping2} is: {bool(mapping2)}")
    print(mapping2)
    print(str(mapping2))
    print(str(mapping1))
