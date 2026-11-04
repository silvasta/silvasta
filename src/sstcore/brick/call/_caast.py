__all__: list[str] = [
    "iter_type_hints",
    "build_plan",
    "param_spec",
    "typed_dict",
    "cast_mapping",
]

import typing as _t
from collections.abc import Callable, Iterator, MutableMapping
from inspect import BoundArguments, Parameter, Signature
from typing import Annotated, Any, Unpack

from ...port.casting import ArgCasting, CastPlan, TypeRegistry


def iter_type_hints(target: Callable | type, /) -> Iterator[tuple[str, Any]]:
    """Yield (name, annotation) and recursively unpack TypedDicts."""
    # Unwrap generic aliases (e.g., SafeFunctorInput[Args, Result] -> SafeFunctorInput)
    origin_target = _t.get_origin(target) or target

    for name, hint in _t.get_type_hints(
        origin_target, include_extras=True
    ).items():
        if name == "return":
            continue

        if _t.get_origin(hint) is Unpack:
            unpacked = _t.get_args(hint)[0]
            yield from iter_type_hints(unpacked)
        else:
            yield name, hint


def build_plan(
    target: Callable[..., Any] | type[Any],
    registry: TypeRegistry,
    /,
) -> CastPlan:
    """
    Match Annotations with explicit Annotated ArgCasting or fallback to Registry.

    Priority:
    1. First ArgCasting found in Annotated[T, ...] metadata
    2. Base type T of Annotated[T, ...] if T is in registry
    3. Direct annotation T if T is in registry
    """
    plan: CastPlan = {}

    for name, annotation in iter_type_hints(target):
        if _t.get_origin(annotation) is Annotated:
            args = _t.get_args(annotation)
            # 1. Explicit caster in metadata
            for meta in args[1:]:
                if isinstance(meta, ArgCasting):
                    plan[name] = meta
                    break
            else:
                # 2. Fallback to base type of Annotated[base_type, ...]
                if (base_type := args[0]) in registry:
                    plan[name] = registry[base_type]

        # 3. Direct registered type (e.g., Path, PathArg, SyncMode, ColorArg)
        elif annotation in registry:
            plan[name] = registry[annotation]

    return plan


def param_spec(
    plan: CastPlan, bound: BoundArguments, sig: Signature, /
) -> None:
    """Cast regular Positional and Keyword Arguments."""
    for name in plan.keys() & bound.arguments.keys():
        param: Parameter = sig.parameters[name]

        if param.kind is Parameter.VAR_KEYWORD:
            continue

        val = bound.arguments[name]
        bound.arguments[name] = (
            plan[name](val)
            if param.default is Parameter.empty
            else plan[name](val, default=param.default)
        )


def typed_dict(
    plan: CastPlan, bound: BoundArguments, sig: Signature, /
) -> None:
    """Cast unpacked TypedDict entries inside **kwargs (VAR_KEYWORD) in-place."""
    for name, param in sig.parameters.items():
        if param.kind is Parameter.VAR_KEYWORD:
            if kw := bound.arguments.get(name):
                cast_mapping(plan, kw)
            return


def cast_mapping(plan: CastPlan, data: MutableMapping[str, Any], /) -> None:
    """Apply a CastPlan directly to a mutable mapping in-place."""
    for key in plan.keys() & data.keys():
        data[key] = plan[key](data[key])
