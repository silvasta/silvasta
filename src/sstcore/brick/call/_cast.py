"""
Intercept Function Input and Apply Rules before Entry

- inspect typing.Annotated in signatures and extract rules
- unpack typing.TypedDict and apply rules to flattened params

What is the meaning of "cast" in this context?
- active process of enforcing rules to signatures
  (not equivalent to typing.cast but useful)

"""

__all__: list[str] = [
    "iter_type_hints",
    #
    "param_spec",
    "typed_dict",
]


import dataclasses as _dc
import typing as _t
from collections.abc import Callable, Iterator, MutableMapping
from inspect import BoundArguments, Parameter, Signature
from typing import Any, Unpack

from ...port.casting import ArgCasting, CastPlan, SpecBase


def pack_prefixed[P: SpecBase](
    # NEXT: where to use this?
    kwargs: dict,
    prefix: str,
    spec_cls: type[P],
) -> P | None:
    picked = {
        k.removeprefix(prefix): kwargs.pop(k)
        for k in list(kwargs)
        if k.startswith(prefix)
    }
    return spec_cls(**picked) if picked else None


def partition_fields(spec: SpecBase, *spec_clses: type) -> dict[str, dict]:
    # NEXT: where to use this?
    """Обобщенный аналог extract_base: разделить поля спецификации по их базовым классам."""
    return {
        cls.__name__: {f.name: getattr(spec, f.name) for f in _dc.fields(cls)}
        for cls in spec_clses
    }


def iter_type_hints(target: Callable | type, /) -> Iterator[tuple[str, Any]]:
    # LATER: move to _inspect? or .._reflect?
    """Yield (name, annotation) and if needed unpacke TypedDict"""

    for name, hint in _t.get_type_hints(target, include_extras=True).items():
        if name == "return":  # reject annotation of return type for casting
            continue

        if _t.get_origin(hint) is Unpack:
            yield from iter_type_hints(_t.get_args(hint)[0])

        else:
            yield name, hint


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def find_annotated_caster(plan: CastPlan, name: str, annotation) -> None:
    """Iterate over Annotated metadata and register first Hit"""
    for caster in _t.get_args(annotation)[1:]:
        if isinstance(caster, ArgCasting):
            plan[name] = caster
            return


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


def typed_dict(plan: CastPlan, bound: BoundArguments):
    """Unpack and Cast TypedDict inside bound.kwargs"""

    if kw := bound.kwargs:
        for key in plan.keys() & kw.keys():
            kw[key] = plan[key](kw[key])  # FIX:


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
