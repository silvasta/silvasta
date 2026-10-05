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
from inspect import Signature, signature
from typing import Any, Self

from ...port import attach
from ...port.calling import Calling
from ...port.link import portlink
from ._decorate import DecoratedField
from ._extend import ResetField


class MethodFieldEngine[**In, Out](DecoratedField[In, Out], ResetField):
    """Base Engine for dynamic Calling fields."""

    def __init__(self, func: Calling[In, Out], *args: Any, **kwargs: Any):
        # 'func' maps to 'DecoratedField.target_func'
        super().__init__(func, *args, default=func, **kwargs)

    def read(self, unit: object) -> BoundStrategy[In, Out]:
        """Intercept read to return a self-aware Proxy instead of raw func."""

        if self._has_val(unit):
            func: Calling[In, Out] = self._get_val(unit)
        else:
            func: Calling[In, Out] = self.target_func

        return BoundStrategy[In, Out](self, unit, func)


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](MethodFieldEngine[In, Out]):
    """Forces the override to match the default function's signature."""

    def switch(self, func: Calling[In, Out]) -> Self:
        """Modify the Class-Level baseline strategy."""
        self.bind(func)
        return self

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
    ):
        self.engine: MethodFieldEngine[In, Out] = engine
        self.unit: Any = unit
        self.func: Calling[In, Out] = func

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        return self.func(self.unit, *args, **kwargs)

    def switch(self, new_func: Calling[In, Out]) -> Self:
        """LSP-compliant function swap for this instance only."""
        self.engine.write(self.unit, new_func)
        self.func: Calling[In, Out] = new_func
        return self

    def morph[**P, R](self, new_func: Calling[P, R]) -> Self:
        """Unsafe/LSP-violating function swap for this instance only."""
        if hasattr(self.engine, "morph"):
            self.engine.write(self.unit, new_func)
            self.func: Calling[P, R] = new_func
            return self
        raise TypeError("Morphing not supported on strict StrategyField.")


def _check_sig_param_length(sig1: Signature, sig2: Signature) -> bool:
    """Compare argument counts for strict strategy swapping."""
    return len(sig1.parameters) == len(sig2.parameters)


def _valid_sig(func: Callable, baseline: Signature) -> bool:
    """Ensure the new callable adheres to the expected baseline."""
    try:
        new_sig: Signature = signature(func)
    except ValueError:
        return False

    checks_ok: list[bool] = [
        _check_sig_param_length(new_sig, baseline),
        # LATER: Extend with type-hint matching (Liskov Substitution checks)
    ]
    return all(checks_ok)
