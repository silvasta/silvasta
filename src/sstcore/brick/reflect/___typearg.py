"""
Type Test

.
"""

from typing import Any, ParamSpec, TypeIs, TypeVarTuple, get_args

#  LINE: -- Currently Used -- -- - -- -- - -- -- - -- -- - -- -- - -- --

_CURRENT_VARIADICS = (ParamSpec, TypeVarTuple)
_CURRENT_VARIADICS_ = ParamSpec | TypeVarTuple


def is_variadic(target: Any, /) -> TypeIs[_CURRENT_VARIADICS_]:
    return isinstance(target, _CURRENT_VARIADICS)


def _is_variadic1(target: Any, /) -> TypeIs[_CURRENT_VARIADICS]:  # AI: issue?
    return isinstance(target, _CURRENT_VARIADICS)  # AI: runtime issue right?


# Option 1: Plain UnionType (works directly in annotations AND isinstance)
type Variadic = ParamSpec | TypeVarTuple
VARIADICS: tuple[type, ...] = get_args(Variadic.__value__)
# -> (<class 'typing.ParamSpec'>, <class 'typing.TypeVarTuple'>)

# Option 2: Direct UnionType variable (no .__value__ needed)
_Variadic = ParamSpec | TypeVarTuple
_VARIADICS: tuple[type, ...] = get_args(_Variadic)

VAR = ParamSpec | TypeVarTuple


def _is_variadic2(target: Any, /) -> TypeIs[Variadic]:
    # FAIL:
    #   File "/home/silvan/PolyBox/Code/sstcore/latest/src/sstcore/brick/reflect/___typearg.py", line 37, in _is_variadic2
    #     return isinstance(target, Variadic)
    # TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union
    return isinstance(target, Variadic)


def _is_variadic3(target: Any, /) -> TypeIs[VARIADICS]:
    return isinstance(target, VARIADICS)


#  LINE: -- ... -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _is_variadic4(target: Any, /) -> TypeIs[Variadic]:
    return isinstance(target, VARIADICS)


def _is_variadic5(target: Any, /) -> TypeIs[_Variadic]:
    return isinstance(target, _VARIADICS)


def _is_variadic6(target: Any, /) -> TypeIs[_VARIADICS]:
    return isinstance(target, _Variadic)


if __name__ == "__main__":
    variadics = [
        is_variadic,
        _is_variadic1,
        # _is_variadic2,
        _is_variadic3,
        _is_variadic4,
        _is_variadic5,
        _is_variadic6,
    ]
    tests = ["hello", 1, ParamSpec("arg1")]
    for is_v in variadics:
        print("\n", f"start of: {is_v.__name__}")
        for test in tests:
            print(f"{test=} is variadic? {is_v(test)}")
