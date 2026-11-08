"""
brick.call._cast

-
"""

__all__: list[str] = [  # TODO: when finished
    "iter_type_hints",
    # "param_spec",
    # "typed_dict",
    # "cast_mapping",
]

import inspect as _inspect
import typing as _t
from collections.abc import Callable, Iterator, MutableMapping
from inspect import BoundArguments, Parameter, Signature
from typing import Annotated, Any, Unpack

from ...port.casting import ArgCasting, CastPlan, CastRegistry
from . import _cast

type Hintable = Callable | type  # CHECK: Castable?

# AI_TASK: here is like the collecion of everything discovered so far, it needs to be finalized
# - iter hints: probably fine as it is
# - casting: here are multiple approaches, nice would be having topics separated, e.g. cast regular params or cast typed dicts, ...
#   - final assembly of all parts here or in ._argcast, preferably there if possible
#   - in the end 1 proper function that launches the execution is fine
# - build_plan: check if some of the _walk has something useful and assemble the best parts


#  LINE: -- iter hints -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def iter_type_hints(target: Hintable, /) -> Iterator[tuple[str, Any]]:
    """Yield (Name,Annotation) and unpack TypedDicts recursively"""

    for name, hint in type_hints_from_origin(target):
        if name == "return":
            continue

        if _t.get_origin(hint) is Unpack:
            _unpacked = _t.get_args(hint)[0]
            yield from iter_type_hints(_unpacked)

        else:
            yield name, hint


# CHECK: private? or expose?
def type_hints_from_origin(target: Hintable, /) -> Iterator[tuple[str, Any]]:
    """Unwrap Generic Aliases (FunctorInput[Args, Result] -> FunctorInput)"""
    _origin = _t.get_origin(target) or target
    yield from _t.get_type_hints(_origin, include_extras=True).items()


#  LINE: -- casting functions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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


#  LINE: -- build_plan for ArgCast.walk -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _walk(target: Callable[..., Any] | type[Any], /) -> CastPlan:
    """
    Map all Signatures to their Annotated resolver

    - reversed: first Caster overwrites any subsequent ones
    """
    return {  # LATER: decompose fragments and assemble, eg PathSpec
        name: caster
        for name, annotation in iter_type_hints(target)
        if _t.get_origin(annotation) is Annotated
        for caster in reversed(_t.get_args(annotation)[1:])
        if isinstance(caster, ArgCasting)
    }


def _walk(cls, target: Callable[..., Any] | type[Any], /) -> CastPlan:
    """Compile a CastPlan for a function, dataclass, or TypedDict."""
    return build_plan(target, cls._registry)


def build_plan(
    target: Callable[..., Any] | type[Any],
    registry: CastRegistry,
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

    for name, annotation in _cast.iter_type_hints(target):
        if _t.get_origin(annotation) is Annotated:
            _args = _t.get_args(annotation)
            # 1. Explicit caster in metadata
            for meta in _args[1:]:
                if isinstance(meta, ArgCasting):
                    plan[name] = meta
                    break
            else:
                # 2. Fallback to base type of Annotated[base_type, ...]
                if (base_type := _args[0]) in registry:
                    plan[name] = registry[base_type]

        # 3. Direct registered type (e.g., Path, PathArg, SyncMode, ColorArg)
        elif annotation in registry:
            plan[name] = registry[annotation]

    return plan


def _walk(self, func) -> dict[str, ArgCasting]:
    plan: dict[str, ArgCasting] = {}
    for name, param in _inspect.signature(func).parameters.items():
        if param.kind is not Parameter.VAR_KEYWORD:
            continue
        ann = param.annotation
        if _t.get_origin(ann) is Unpack and (
            c := self._registry.get(_t.get_args(ann)[0])
        ):
            plan[name] = c
    return plan


def _walk(self, target, /) -> CastPlan:
    plan: CastPlan = {}
    for name, annotation in _cast.iter_type_hints(target):
        if _t.get_origin(annotation) is Annotated:
            find_annotated_caster(plan, name, annotation)
            if name not in plan:
                self._fallback(plan, name, annotation)
        elif caster := self._registry.get(annotation):
            plan[name] = caster
    return plan
