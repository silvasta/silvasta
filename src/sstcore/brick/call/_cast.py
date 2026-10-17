"""
Intercept Function Input and Apply Rules before Entry

- inspect typing.Annotated in signatures and extract rules
- unpack typing.TypedDict and apply rules to flattened params

What is the meaning of "cast" in this context?
- active process of enforcing rules to signatures
  (not equivalent to typing.cast but useful)

"""

# TASK: Registry
# - no import of sstcore.brick.vault.* as core of registry here!
# - assemble in sstcore.forge.func, maybe with additional later on registration
# - use a new data type that allows for standardized Type handling:
#   - something like a toggle for sure, some statistics
# - registry:
#   - ensures or warns for (not) loaded entries
#   - shows explanation short and clear or detailed on request
# - overall ensure that nothing is casted that is not wanted,
#   and as many options are easily selectable as possible

# IDEA: make each item a Rule:
# - each Rule has a name, a field in Spec and Input and a resolver
# - maybe even as some IntFlag that can be switched fast

# TASK: Components
# - CastInput: TypedDict kwargs
# - CastSpec: holds validation and confirmed data of 1 interception
#   data-structure ideas:
#     - (auto-)dataclass with normalize/validate(/sanitize)
#     - registry with flags: each flag corresponds to 1 casting rule
# - ArgCaster: the loop function:
#   - executes (spec-)validation or regular function, mapped in ArgCast
#   - maybe some caching, preparing new values from ArgCast for CastSpec

# TASK: Main
# - ArgCast: orchestrate plan generation, global registry and decorator
#   - keep plan extendable by subclasses but with guided execution
#   - use BisectRegistry for different changeable levels of casting
#     - maybe CasterRegistry containing FlagRuleRegistries per topic
# - later: check all hybrid combinations of cls, unit, even meta

__all__: list[str] = [
    "ArgCast",
    "ArgCasting",
    "castarg",
    "CastPlan",
    "iter_type_hints",
]


import functools
import inspect as _inspect
import typing as _t
from collections.abc import Callable, Iterator
from inspect import BoundArguments, Parameter, Signature
from typing import Annotated, Any, Protocol, Unpack

from ...brick.none import UNSET

x: UNSET


class ArgCast:
    """Cast Arguments in Function Signature"""

    pass_defaults: bool = True
    type_registry: dict[type, ArgCasting] = {}  # CHECK: on class or unit?
    # LATER: develop registry in forge.func with brick.vault.* + brick.call.*

    def __init__(
        self, *, pass_defaults: bool | None = None, **overrides: ArgCasting
    ) -> None:
        if pass_defaults is not None:
            self.pass_defaults: bool = pass_defaults
        self.overrides: CastPlan = overrides

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        """Compile CastPlan once at Startup for continuous Execution"""

        plan: CastPlan = self.walk_plan(func) | self.overrides

        if not plan:
            return func

        signature: Signature = _inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            bound: BoundArguments = signature.bind(*args, **kwargs)

            if self.pass_defaults:
                bound.apply_defaults()

            _cast_param_spec(plan, bound, signature)
            _cast_typed_dict(plan, bound)

            return func(*bound.args, **bound.kwargs)

        return wrapper

    @staticmethod
    def walk_plan(target: Callable[..., Any] | type[Any], /) -> CastPlan:
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


castarg = ArgCast()  # TARGET: main result for export


type CastPlan = dict[str, ArgCasting]
type _Coerce[T] = T | Any
type _Optional[T] = T | type[Parameter.empty]


@_t.runtime_checkable
class ArgCasting(Protocol):
    """Check if target can be used for ArgCast pipeline"""

    def __call__[T](
        self,
        target: _Coerce[T],
        /,
        *,
        # LATER: check if this will ever be changed by ArgCast during runtime
        # - if this is changed, why not others? Functor pattern with mutable config
        # - if this always runs in a loop without any external access, delete, add on subclass or so
        #   - or keep for pure functions that don't have other storage?
        default: _Optional[T] = Parameter.empty,
    ) -> T:
        """Cast, Coerce, Resolve and or Validate the Function Input"""


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


#  LINE: -- Helpers -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _cast_param_spec(plan: CastPlan, bound: BoundArguments, sig: Signature, /):
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


def _cast_typed_dict(plan: CastPlan, bound: BoundArguments):
    """Unpack and Cast TypedDict inside bound.kwargs"""

    if kw := bound.kwargs:
        for key in plan.keys() & kw.keys():
            kw[key] = plan[key](kw[key])
