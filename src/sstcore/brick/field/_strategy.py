"""
Exchange Callables on Classes

- StrategyField:
                                                 DependencyLevel[3]
"""

__all__: list[str] = [
    "StrategyField",
    "MorphingField",
    #
    "MethodFieldEngine",
    "BoundStrategy",
]

from collections.abc import Callable
from inspect import Parameter, Signature, signature
from typing import Any, Self

from ...port import attach
from ...port.calling import Calling
from ...port.link import portlink
from ._decorate import DecoratedField
from ._extend import ResetField


# AI_FOCUS: when are strategy() and morphing() applied?
def strategy[F: Callable](func: F) -> F:
    """Identity marker. Metaclass mounts a StrategyField; ty still sees a method."""
    func.__field_kind__ = StrategyField  # ty:ignore
    return func


# AI_FOCUS: when are strategy() and morphing() applied?
def morphing[F: Callable](func: F) -> F:
    func.__field_kind__ = MorphingField  # ty:ignore
    return func


class MethodFieldEngine[**In, Out](DecoratedField[In, Out], ResetField):
    """Base Engine for dynamic Calling fields."""

    def __init__(
        self,
        func: Calling[In, Out],
        *args: Any,
        binds_instance: bool = False,
        **kwargs: Any,
    ):
        """Map func to DecoratedField.target_func"""
        self.binds_instance: bool = binds_instance
        default: Any = kwargs.pop("default", (func, binds_instance))
        super().__init__(func, *args, default=default, **kwargs)
        if func is not None and binds_instance and self.signature is not None:
            self.signature: Signature = _public_signature(
                func, binds_instance=True
            )

    def write(self, unit: object, value: Calling[In, Out]) -> None:
        # AI: unsure if the tuple with the bool belongs to unit.__dict__
        # - when it is anyway false, why not just use this information?
        _value = self.validate(unit, value)
        self._set_val(unit, (_value, False))

    def read(self, unit: object) -> BoundStrategy[In, Out]:
        if self._has_val(unit):
            _func, _bind = self._get_val(unit)
        elif self.target_func is not None:
            _func, _bind = self.target_func, self.binds_instance
        else:
            raise self.raiser.Function(self, unit, "Missing target_func")
        return BoundStrategy(self, unit, _func, bind=_bind)

    # REMOVE: when new update finished
    # def _read(self, unit: object) -> BoundStrategy[In, Out]:
    #     """Intercept read to return a self-aware Proxy instead of raw func."""
    #     if self._has_val(unit):
    #         func: Calling[In, Out] = self._get_val(unit)
    #         bind = False
    #     elif self.target_func is not None:
    #         func: Calling[In, Out] = self.target_func
    #         bind = True
    #     else:
    #         raise self.raiser.Function(self, unit, "Missing target_func")
    #     return BoundStrategy[In, Out](self, unit, func, bind=bind)

    def switch(self, func: Calling[In, Out]) -> Self:
        """Modify the Class-Level baseline strategy."""
        self.bind(func)
        return self


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](MethodFieldEngine[In, Out]):
    """Forces the override to match the default function's signature."""

    def validate(
        self, unit: object, value: Calling[In, Out]
    ) -> Calling[In, Out]:
        """Enforce strict signature rules for instance-level overrides."""

        if not callable(value):
            raise self.raiser.Function(self, unit, value=value)

        if self.signature is None:  # Fallback if un-bound properly
            raise self.raiser.Signature(self, unit, value=value)

        if not _valid_sig(value, baseline=self.signature):
            raise self.raiser.Signature(self, unit, value=value)

        return value


@portlink(attach.MorphingDescriptor)
class MorphingField[**In, Out](MethodFieldEngine[In, Out]):
    """Allows swapping methods with arbitrary new signatures."""

    def morph(self, func: Calling) -> Self:
        """Unsafe Function Exchange on the Class Level."""
        self.bind(func)
        return self

    def validate(self, unit: object, value: Calling) -> Calling:
        """Permit arbitrary Callings."""
        if not callable(value):
            raise self.raiser.Function(self, unit, value=value)
        return value


class BoundStrategy[**In, Out]:
    """Proxy object that acts as a bound method and provides swap mutations."""

    def __init__(
        self,
        engine: MethodFieldEngine[In, Out],
        unit: object,
        func: Calling[In, Out],
        bind: bool = True,
    ):
        self.engine: MethodFieldEngine[In, Out] = engine
        self.unit: Any = unit
        self.func: Calling[In, Out] = func
        self.bind: bool = bind

    @property
    def __name__(self) -> str:
        return self.func.__name__

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        if self.bind:
            return self.func(self.unit, *args, **kwargs)
        return self.func(*args, **kwargs)

    def switch(self, new_func: Calling[In, Out]) -> Self:
        """LSP-compliant function swap for this instance only."""
        self.engine.write(self.unit, new_func)
        self.func: Calling[In, Out] = new_func
        self.bind = False
        return self

    def morph[**P, R](self, new_func: Calling[P, R]) -> Self:
        """Unsafe/LSP-violating function swap for this instance only."""
        if hasattr(self.engine, "morph"):
            self.engine.write(self.unit, new_func)
            self.func: Calling[P, R] = new_func
            return self
        raise TypeError("Morphing not supported on strict StrategyField.")


def _valid_sig(func: Callable, baseline: Signature) -> bool:
    try:
        new_sig: Signature = signature(func)
    except ValueError:
        return False

    checks_ok: list[bool] = [
        _is_open_signature(baseline),
        _check_sig_param_length(new_sig, baseline),
        # LATER: Extend list maybe by level
        # (Liskov Substitution checks)
    ]
    return all(checks_ok)


def _check_sig_param_length(sig1: Signature, sig2: Signature) -> bool:
    """Compare argument counts for strict strategy swapping."""
    sig1_clean: Signature = _strip_self(sig1)
    sig2_clean: Signature = _strip_self(sig2)
    return len(sig1_clean.parameters) == len(sig2_clean.parameters)


def _strip_self(sig: Signature) -> Signature:
    """Helper to remove 'self' from signature for fair comparison."""
    params: list[Parameter] = list(sig.parameters.values())
    if params and params[0].name in ("self", "cls"):
        return sig.replace(parameters=params[1:])
    return sig


def _public_signature(func: Callable, *, binds_instance: bool) -> Signature:
    sig: Signature = signature(func)
    if not binds_instance:
        return sig
    params: list[Parameter] = list(sig.parameters.values())
    if params and params[0].kind in (
        Parameter.POSITIONAL_ONLY,
        Parameter.POSITIONAL_OR_KEYWORD,
    ):
        params: list[Parameter] = params[1:]
    return sig.replace(parameters=params)


def _is_open_signature(sig: Signature) -> bool:
    """Placeholder (*args, **kwargs) is not a real contract."""
    kinds = [p.kind for p in sig.parameters.values()]
    return kinds in (
        [],
        [Parameter.VAR_POSITIONAL],
        [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD],
    )
