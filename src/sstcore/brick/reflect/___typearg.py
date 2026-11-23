"""
Type Test

.
"""

from collections.abc import Callable
from typing import (
    Any,
    ParamSpec,
    TypeAliasType,
    TypeIs,
    TypeVarTuple,
    get_args,
    reveal_type,
)

type Variadic = ParamSpec | TypeVarTuple
# EXTRACT:
VARIADICS: tuple[type, ...] = get_args(Variadic.__value__)


def is_variadic(target: Any, /) -> TypeIs[Variadic]:
    # EXTRACT:
    # EXTRACT:
    return isinstance(target, get_args(Variadic.__value__))


def unpack_type(target: TypeAliasType, /) -> tuple[type, ...]:
    # EXTRACT:
    # EXTRACT:
    reveal_type(target)
    return (
        get_args(target.__value__)
        if hasattr(target, "__value__")
        else (target,)
        if isinstance(target, type)
        else (type(target),)
    )


reveal_type(unpack_type(Variadic))
reveal_type(unpack_type(VARIADICS))
reveal_type(unpack_type("str"))


if __name__ == "__main__":
    variadics: list[Callable] = [
        is_variadic,
        unpack_type,
    ]
    tests = ["hello", 1, ParamSpec("arg1")]
    for is_v in variadics:
        print("\n", f"start of: {is_v.__name__}")
        for test in tests:
            print(f"{test=} is variadic? {is_v(test)}")
