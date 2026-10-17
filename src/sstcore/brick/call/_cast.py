"""
Intercept Function Input and Apply Rules before Entry

- inspect typing.Annotated in signatures and extract rules
- unpack typing.TypedDict and apply rules to flattened params

What is the meaning of "cast" in this context?
- active process of enforcing rules to signatures
  (not equivalent to typing.cast but useful)

"""

__all__: list[str] = [
    "ArgCaster",
    "ArgCast",
    "castarg",
]


import functools
import inspect as _inspect
import typing as _t
from collections.abc import Callable, Iterator
from inspect import BoundArguments, Parameter, Signature
from typing import Annotated, Any, Protocol, Unpack


@_t.runtime_checkable
class ArgCaster(Protocol):
    """Check if target can be used for ArgCast pipeline"""

    def __call__[T](
        self, value: _Coerce[T], /, *, default: _Optional[T] = Parameter.empty
    ) -> T:
        """Cast, Coerce, Resolve and or Validate the Function Input"""


type _Coerce[T] = T | Any
type _Optional[T] = T | type[Parameter.empty]
type _CastPlan = dict[str, ArgCaster]


class ArgCast:
    """Cast Arguments in Function Signature"""

    pass_defaults: bool = True
    type_registry: dict[type, ArgCaster] = {}  # CHECK: on class or unit?
    # LATER: define {Path:...} and apply in __call__ or new ArgCast.merge_plan

    def __init__(
        self, *, pass_defaults: bool | None = None, **overrides: ArgCaster
    ) -> None:
        if pass_defaults is not None:
            self.pass_defaults: bool = pass_defaults
        self.overrides: _CastPlan = overrides

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        """Compile CastPlan once at Startup for continuous Execution"""

        if not (plan := self.walk_plan(func) | self.overrides):
            return func

        sig: Signature = _inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            bound: BoundArguments = sig.bind(*args, **kwargs)

            if self.pass_defaults:
                bound.apply_defaults()

            _cast_param_spec(plan, bound, sig)
            _cast_typed_dict(plan, bound)

            return func(*bound.args, **bound.kwargs)

        return wrapper

    @staticmethod
    def walk_plan(target: Callable[..., Any] | type[Any], /) -> _CastPlan:
        """
        Map all Signatures to their Annotated resolver

        - reversed: first Caster overwrites any subsequent ones
        """
        return {
            name: caster
            for name, annotation in _iter_type_hints(target)
            if _t.get_origin(annotation) is Annotated
            for caster in reversed(_t.get_args(annotation)[1:])
            if isinstance(caster, ArgCaster)
        }

    def _walk_plan(
        self, target: Callable[..., Any] | type[Any], /
    ) -> _CastPlan:
        """Map Signatures to Annotated resolver or type_registry fallback"""

        plan: _CastPlan = {}  # NEXT: plan register? add new checks easily

        for name, annotation in _iter_type_hints(target):
            if _t.get_origin(annotation) is Annotated:
                # extract caster for Annotated params
                for caster in reversed(_t.get_args(annotation)[1:]):
                    if isinstance(caster, ArgCaster):
                        plan[name] = caster

                # extract Annotated params without caster but registry entry
                if name not in plan:
                    base_type = _t.get_args(annotation)[0]
                    if base_type in self.type_registry:
                        plan[name] = self.type_registry[base_type]

            # extract regular annotations without caster but registry entry
            elif annotation in self.type_registry:
                plan[name] = self.type_registry[annotation]

        return plan


castarg = ArgCast()  # TARGET: main result for export


#  LINE: -- Helpers -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _cast_param_spec(plan: _CastPlan, bound: BoundArguments, sig: Signature):
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


def _cast_typed_dict(plan: _CastPlan, bound: BoundArguments):
    """Unpack and Cast TypedDict inside bound.kwargs"""

    if kw := bound.kwargs:
        for key in plan.keys() & kw.keys():
            kw[key] = plan[key](kw[key])


def _iter_type_hints(target: Callable | type, /) -> Iterator[tuple[str, Any]]:
    """Yield (name, annotation) and if needed unpacke TypedDict"""

    for name, hint in _t.get_type_hints(target, include_extras=True).items():
        if name == "return":  # reject annotation of return type for casting
            continue

        if _t.get_origin(hint) is Unpack:
            yield from _iter_type_hints(_t.get_args(hint)[0])

        else:
            yield name, hint
