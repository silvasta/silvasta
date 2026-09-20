"""
Exchange Callables on Classes

- StrategyField:
                                                 DependencyLevel[3]
"""

__all__: list[str] = [
    "StrategyField",
    "DynamicStrategy",
]

from collections.abc import Callable
from inspect import Signature, signature
from typing import TYPE_CHECKING, Self

from ...port import attach
from ...port.calling import Calling
from ._decorate import DecoratedField
from ._extend import ResetField


def _check_sig_param_length(sig1, sig2) -> bool:  # MOVE: brick.labor._inspect
    return len(sig1.parameters) == len(sig2.parameters)


def _valid_sig(func: Callable, baseline: Signature) -> bool:  # MOVE: labor
    new_sig: Signature = signature(func)
    checks_ok: list[bool] = [  # LATER: build check box
        _check_sig_param_length(new_sig, baseline),
    ]
    return all(checks_ok)


class BoundStrategy[**In, Out]:
    """Proxy object that acts as a bound method and provides swap mutations."""

    def __init__(
        self, engine: MethodFieldEngine, unit: object, func: Calling[In, Out]
    ):
        self.engine = engine
        self.unit = unit
        self.func = func

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        return self.func(self.unit, *args, **kwargs)

    def switch(self, new_func: Calling[In, Out]) -> None:
        """LSP-compliant function swap."""
        self.engine.write(self.unit, new_func)

    def morph(self, new_func: Callable) -> None:
        """Unsafe/LSP-violating function swap."""
        self.engine.write(self.unit, new_func)


# NEXT: StrategyField
class MethodFieldEngine[**In, Out](DecoratedField, ResetField):
    def __init__(self, default_func: Calling[In, Out], *args, **kwargs):
        # FIX: needed with new FieldDecorator??
        self.default_func = default_func
        super().__init__(*args, default=default_func, **kwargs)

    def read(self, unit: object) -> BoundStrategy[In, Out]:
        func: Calling = (
            self._get_val(unit) if self._has_val(unit) else self.default_func
        )  # FIX:
        # return MethodType(func, unit)
        return BoundStrategy[In, Out](self, unit, func)

    def switch(self, func: Calling[In, Out]) -> Self:
        """Expose new strategy with matching signature"""
        # FIX:
        self.write(unit=instance, value=func)
        return self.read(instance)  # NOTE: unsure how effective that is


# NEXT: MorphingStrategy
class DynamicStrategy(MethodFieldEngine):  # LATER: parametrization?
    """Allows swapping methods with arbitrary new signatures."""

    def morph(self, func: Calling) -> Self:
        """Unsafe Function Exchange"""
        # TODO: check wirirng
        return super().switch(func)

    def validate(self, unit: object, value: Calling) -> Calling:
        # TODO: why is this here? anything to check in this case?
        return super().validate(unit, value)


class StrategyField[**P, R](MethodFieldEngine):
    """Forces the override to match the default function's signature."""

    def validate[T](self, unit: object, value: T) -> T:
        """Finish the loop and return the value"""
        if self.signature is None:
            self.raise_on_signature(unit, bad_func=self.target_func)
        if not _valid_sig(self.target_func, baseline=self.signature):
            self.raise_on_signature(unit, bad_func=value)
        return super().validate(unit, value)


if TYPE_CHECKING:
    _injected: type[attach.CallingDescriptor] = StrategyField
    _injected: type[attach.MorphingDescriptor] = DynamicStrategy
