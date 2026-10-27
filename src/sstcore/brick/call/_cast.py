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


import typing as _t
from collections.abc import Callable, Iterator
from inspect import BoundArguments, Parameter, Signature
from typing import Any, Unpack

from ...port.casting import ArgCasting, CastPlan


def iter_type_hints(target: Callable | type, /) -> Iterator[tuple[str, Any]]:
    # MOVE: _inspect?
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
            kw[key] = plan[key](kw[key])
