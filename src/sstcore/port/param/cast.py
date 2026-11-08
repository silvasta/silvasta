"""
brick.call._cast

-
"""

__all__: list[str] = [  # TODO: when finished
    # "iter_type_hints",
    "param_spec",
    # "typed_dict",
    "cast_mapping",
]

import typing as _t
from collections.abc import Callable, Iterator, MutableMapping
from inspect import BoundArguments, Parameter, Signature
from typing import Any, Unpack

from .casting import ArgCasting, CastPlan


def _iter_type_hints(target: Callable | type, /) -> Iterator[tuple[str, Any]]:
    # LATER: move to _inspect? or .._reflect?
    """Yield (name, annotation) and if needed unpacke TypedDict"""

    for name, hint in _t.get_type_hints(target, include_extras=True).items():
        if name == "return":  # reject annotation of return type for casting
            continue

        if _t.get_origin(hint) is Unpack:
            yield from _iter_type_hints(_t.get_args(hint)[0])

        else:
            yield name, hint


def _iter_type_hints(target: Callable | type, /) -> Iterator[tuple[str, Any]]:
    """Yield name,annotation and recursively unpack TypedDicts"""

    # Unwrap generic aliases (e.g., SafeFunctorInput[Args, Result] -> SafeFunctorInput)
    _origin_target = _t.get_origin(target) or target

    for name, hint in _t.get_type_hints(
        _origin_target, include_extras=True
    ).items():
        if name == "return":
            continue

        if _t.get_origin(hint) is Unpack:
            unpacked = _t.get_args(hint)[0]
            yield from _iter_type_hints(unpacked)
        else:
            yield name, hint


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _typed_dict(
    plan: CastPlan, bound: BoundArguments, sig: Signature, /
) -> None:
    """Cast unpacked TypedDict entries inside **kwargs (VAR_KEYWORD) in-place."""
    for name, param in sig.parameters.items():
        if param.kind is Parameter.VAR_KEYWORD:
            if kw := bound.arguments.get(name):
                cast_mapping(plan, kw)
            return


def _typed_dict(plan: CastPlan, bound: BoundArguments):
    """Unpack and Cast TypedDict inside bound.kwargs"""

    if kw := bound.kwargs:
        for key in plan.keys() & kw.keys():
            kw[key] = plan[key](kw[key])  # FIX:


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def param_spec(plan: CastPlan, bound: BoundArguments, sig: Signature, /):
    """Cast regular Positional and Keyword Arguments"""

    for name in plan.keys() & bound.arguments.keys():
        param: Parameter = sig.parameters[name]

        if param.kind is Parameter.VAR_KEYWORD:
            continue

        bound.arguments[name] = (
            plan[name](bound.arguments[name])
            if param.default is Parameter.empty
            else plan[name](bound.arguments[name], default=param.default)
        )


def cast_mapping(plan: CastPlan, data: MutableMapping[str, Any], /) -> None:
    """Apply a CastPlan directly to a mutable mapping in-place."""
    for key in plan.keys() & data.keys():
        data[key] = plan[key](data[key])


def find_annotated_caster(plan: CastPlan, name: str, annotation) -> None:
    """Iterate over Annotated metadata and register first Hit"""
    for caster in _t.get_args(annotation)[1:]:
        if isinstance(caster, ArgCasting):
            plan[name] = caster
            return


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def apply_mapping(plan: CastPlan, data: MutableMapping[str, Any]) -> None:
    for key in plan.keys() & data.keys():
        data[key] = plan[key](data[key])


def apply_bound(plan: CastPlan, bound: BoundArguments, sig: Signature) -> None:
    for name in plan.keys() & bound.arguments.keys():
        param = sig.parameters[name]
        if param.kind is Parameter.VAR_KEYWORD:
            apply_mapping(plan, bound.arguments[name])
            continue
        value = bound.arguments[name]
        if param.default is Parameter.empty:
            bound.arguments[name] = plan[name](value)
        else:
            bound.arguments[name] = plan[name](value, default=param.default)
