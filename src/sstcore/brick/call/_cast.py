"""
brick.call._cast

-
"""

__all__: list[str] = [
    "find_annotated_caster",
    "resolve_caster",
    "build_plan",
    "mapping",
    "param_spec",
    "typed_dict",
]

import typing as _t
from inspect import BoundArguments, Parameter
from typing import Annotated, Any, NotRequired, Required

from ...port._types import CallingTypes as _CT  # noqa: N814
from ...port._types import _ArgCasting as ArgCasting
from ...port.empty import MayNot
from ..reflect._typehint import iter_type_hints


def build_plan(
    target: _CT.Castable, registry: _CT.CastRegistry, /
) -> _CT.CastPlan:
    """Match target annotations with explicit Annotated casters or fallback to Registry."""
    return {
        name: caster
        for name, annotation in iter_type_hints(target)
        if (caster := resolve_caster(annotation, registry)) is not None
    }


def resolve_caster(
    annotation: Any, registry: _CT.CastRegistry, /
) -> MayNot[ArgCasting]:
    """
    Resolve a single type annotation to an ArgCasting instance.

    Priority:
    1. Unwrap TypedDict Required / NotRequired wrappers if present
    2. First ArgCasting found in Annotated[T, ...] metadata
    3. Base type T of Annotated[T, ...] if T is in registry
    4. Direct annotation T if T is in registry
    """
    if annotation in registry:
        return registry[annotation]

    while isinstance(annotation, _t.TypeAliasType):
        annotation = annotation.__value__
        if annotation in registry:
            return registry[annotation]

    if _t.get_origin(annotation) in (Required, NotRequired):
        annotation = _t.get_args(annotation)[0]

    if _t.get_origin(annotation) is Annotated:
        if (caster := find_annotated_caster(annotation)) is not None:
            return caster
        annotation = _t.get_args(annotation)[0]

    return registry.get(annotation)


def find_annotated_caster(annotation: Any, /) -> MayNot[ArgCasting]:
    """Iterate over Annotated metadata and provide first Caster"""
    for meta in _t.get_args(annotation)[1:]:
        if isinstance(meta, ArgCasting):
            return meta


def mapping(plan: _CT.CastPlan, data: _CT.Data, /) -> None:
    """Apply CastPlan directly to mutable mapping in-place"""
    for key in plan.keys() & data.keys():
        data[key] = plan[key](data[key])


def param_spec(plan: _CT.CastPlan, bound: BoundArguments, /) -> None:
    """Cast regular Positional and Keyword Arguments in BoundArguments"""

    for name in plan.keys() & bound.arguments.keys():
        param: Parameter = bound.signature.parameters[name]

        if param.kind is Parameter.VAR_KEYWORD:
            continue

        bound.arguments[name] = (
            plan[name](bound.arguments[name])
            if param.default is Parameter.empty
            else plan[name](bound.arguments[name], default=param.default)
        )


def typed_dict(plan: _CT.CastPlan, bound: BoundArguments, /) -> None:
    """Cast VAR_KEYWORD (**kwargs / Unpack[TypedDict]) in BoundArguments"""

    for name, param in bound.signature.parameters.items():
        if param.kind is not Parameter.VAR_KEYWORD:
            continue

        if (kw_data := bound.arguments.get(name)) is not None:
            # 1. Cast flattened TypedDict fields (or extra kwargs casters)
            mapping(plan, kw_data)
            # 2. Apply whole-dict caster if registered for TypedDict
            if name in plan:
                bound.arguments[name] = plan[name](kw_data)
        return
