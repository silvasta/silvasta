"""
Exchange Callables on Classes

- StrategyField:
                                                 DependencyLevel[1]
"""

__all__: list[str] = [
    "StrategyField",
    "DynamicStrategy",
]

from collections.abc import Callable
from inspect import Signature, signature
from types import MethodType
from typing import TYPE_CHECKING, Any, Self

from ...port import attach
from ...port.calling import Calling
from ._specify import DecoratedField, ResetField

# INFO:
# class Calling[**In, Out](Protocol):
#     @property
#     def __name__(self) -> str: ...
#     def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out: ...


# MOVE: after impement finish, brick.labor.inspect
def _check_sig_param_length(sig1, sig2) -> bool:
    return len(sig1.parameters) == len(sig2.parameters)


# MOVE: after impement finish, brick.labor.inspect
def _valid_sig(func: Callable, baseline: Signature) -> bool:
    new_sig: Signature = signature(func)
    checks_ok: list[bool] = [  # LATER: build check box
        _check_sig_param_length(new_sig, baseline),
    ]
    # return new_sig if all(checks_ok) else None
    return all(checks_ok)


# NEXT:
class MethodFieldEngine[**In, Out](DecoratedField, ResetField):
    def __init__(self, default_func: Calling[In, Out], *args, **kwargs):
        # REMOVE: needed with new FieldDecorator??
        self.default_func = default_func
        super().__init__(*args, default=default_func, **kwargs)

    def read(self, unit: object) -> Any:
        # TODO: check if parametrization here makes sense
        # NOTE: maybe no param here for case: lsp violation
        func: Calling = (
            self._get_val(unit) if self._has_val(unit) else self.default_func
        )
        return MethodType(func, unit)

    def validate[T](self, unit: object, value: T) -> T:
        """Finish the loop and return the value"""
        if self.signature is None:
            self.raise_on_signature(unit, bad_func=self.target_func)
        if not _valid_sig(self.target_func, baseline=self.signature):
            self.raise_on_signature(unit, bad_func=value)
        return super().validate(unit, value)

    def switch(self, func: Calling[In, Out]) -> Self:
        """Expose new strategy with matching signature"""
        # IMPORTANT: how to get the unit=instance here?
        # - load at init? but who inserts? get from super()?
        # - safe to store an internal reference to the unit?
        self.write(unit=instance, value=func)
        return self.read(instance)  # NOTE: unsure how effective that is


# NEXT:
class DynamicStrategy(MethodFieldEngine):
    """Allows swapping methods with arbitrary new signatures."""

    def morph(self, func: Calling) -> Self:
        """Unsafe Function Exchange"""
        # TODO: check wirirng
        return super().switch(func)

    def validate(self, unit: object, value: Calling) -> Calling:
        # TODO: why is this here? anything to check in this case?
        return super().validate(unit, value)


# NEXT:
class StrategyField[**P, R](MethodFieldEngine):
    """Forces the override to match the default function's signature."""

    # AI_FOCUS: this is the main target

    def __init__(self, default_func: Calling[P, R], *args, **kwargs):
        # TODO: catch signature from original function
        super().__init__(default_func, *args, **kwargs)

    def validate(self, unit: object, value: Calling[P, R]) -> Calling[P, R]:
        # TODO: check signature from original function
        return super().validate(unit, value)


if TYPE_CHECKING:
    _injected: type[attach.CallingDescriptor] = StrategyField
    _injected: type[attach.MorphingDescriptor] = DynamicStrategy
