"""
Replace callables on a class or instance.

- StrategyField: replacements must match the baseline signature (LSP)
- MorphingField: replacements may violate that signature
                                                 DependencyLevel[2]
"""

__all__: list[str] = [
    "StrategyField",
    "MorphingField",
    "BoundStrategy",
]

from collections.abc import Callable
from inspect import Signature, signature
from types import MethodType
from typing import Any, Self

from ...port import attach
from ...port.calling import Calling
from ...port.link import portlink
from ._decorate import DecoratedField
from ._extend import ResetField


class MethodFieldEngine[**In, Out](DecoratedField[In, Out], ResetField):
    """
    Shared engine for swappable callables. (g46)

    Reuses FieldDecorator.bind for @usage and signature capture.
    Overrides DecoratedField.read (no cached MethodType) and
    FieldDecorator.validate (must allow rewrite — that is the point).
    """

    allow_morph: bool = False
    strict_write: bool = True
    bind_self: bool

    def __init__(
        self,
        func: Calling[In, Out] | None = None,
        *args: Any,
        bind_self: bool = True,
        **kwargs: Any,
    ) -> None:
        self.bind_self = bind_self
        super().__init__(func, *args, **kwargs)

    def read(
        self, unit: object
    ) -> BoundStrategy[In, Out] | Calling[In, Out] | None:
        func: Calling[In, Out] | None = (
            self._get_val(unit) if self._has_val(unit) else self.target_func
        )
        if func is None:
            return None
        if self.bind_self:
            return BoundStrategy[In, Out](self, unit, func)
        return func

    def validate(self, unit: object, value: Any) -> Any:
        """Allow rewrite. FieldDecorator.validate is write-once — skip it."""
        value = _unwrap(value)

        if value is None:
            if self.target_func is not None:
                raise self.raiser.Function(self, unit, value=value)
            return value

        if not callable(value):
            raise self.raiser.Function(self, unit, value=value)

        self._check_replacement(unit, value)
        return value

    def switch(self, func: Calling[In, Out]) -> Self:
        """Replace the class-level default (LSP)."""
        self.assert_lsp(func, unit=None)
        self.bind(func)
        return self

    def assert_lsp(self, func: Callable, unit: object | None = None) -> None:
        if self.signature is None:
            return
        if not callable(func) or not _valid_sig(func, self.signature):
            raise self.raiser.Signature(self, unit, value=func)

    def _capture_sig(self, func: Callable) -> None:
        if self.signature is not None:
            return
        try:
            self.signature = signature(func)
        except TypeError, ValueError:
            return

    def _check_replacement(self, unit: object, value: Callable) -> None:
        if self.signature is None:
            self._capture_sig(value)
            return
        if self.strict_write:
            self.assert_lsp(value, unit)


@portlink(attach.CallingDescriptor)
class StrategyField[**In, Out](MethodFieldEngine[In, Out]):
    """
    Swappable callable with LSP enforcement.

    Method (default — binds instance)::

        class Renderer:
            @StrategyField
            def render(self, frame: int) -> str:
                return f"default:{frame}"

        r = Renderer()
        r.render(3)                          # "default:3"
        r.render.switch(lambda self, frame: f"gl:{frame}")
        r.render(3)                          # "gl:3"

    Callback value (no self — vault ident)::

        class BaseVault:
            _ident = StrategyField(bind_self=False)

        v._ident = lambda item: item.id      # assignment, keeps `is None`
        v._ident(item)                       # item.id
    """

    strict_write = True
    allow_morph = False


@portlink(attach.MorphingDescriptor)
class MorphingField[**In, Out](MethodFieldEngine[In, Out]):
    """
    Swappable callable without LSP enforcement on write.

    `switch` still checks the baseline when one exists.
    `morph` / assignment may change the signature.
    """

    strict_write = False
    allow_morph = True

    def morph(self, func: Calling) -> Self:
        """Replace the class-level default without a signature check."""
        self.bind(func)
        return self


class BoundStrategy[**In, Out]:
    """Instance handle: call the current strategy and replace it."""

    def __init__(
        self,
        engine: MethodFieldEngine[In, Out],
        unit: object,
        func: Calling[In, Out],
    ) -> None:
        self.engine = engine
        self.unit = unit
        self.func = func
        self.__name__ = getattr(func, "__name__", "strategy")
        self.__doc__ = getattr(func, "__doc__", None)
        self.__wrapped__ = func

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out:
        return self.func(self.unit, *args, **kwargs)

    def switch(self, new_func: Calling[In, Out]) -> Self:
        """LSP-compliant swap for this instance."""
        self.engine.assert_lsp(new_func, self.unit)
        self.engine.write(self.unit, new_func)
        self.func = new_func
        return self

    def morph(self, new_func: Callable) -> Self:
        """Signature-free swap. Only MorphingField allows this."""
        if not self.engine.allow_morph:
            raise self.engine.raiser.Signature(
                self.engine, self.unit, value=new_func
            )
        self.engine.write(self.unit, new_func)
        self.func = new_func
        return self

    def __repr__(self) -> str:
        return f"<BoundStrategy {self.__name__} of {self.engine}>"


def _param_count(sig: Signature) -> int:  # MOVE: brick.labor._inspect
    return len(sig.parameters)


def _valid_sig(func: Callable, baseline: Signature) -> bool:  # MOVE: labor
    try:
        new_sig = signature(func)
    except TypeError, ValueError:
        return False
    checks_ok: list[bool] = [  # LATER: names, kinds, annotations
        _param_count(new_sig) == _param_count(baseline),
    ]
    return all(checks_ok)


def _unwrap(value: Any) -> Any:
    """Store the raw function, never a bound proxy."""
    if isinstance(value, BoundStrategy):
        return value.func
    if isinstance(value, MethodType):
        return value.__func__
    return value
