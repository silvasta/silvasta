"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

__all__: list[str] = [
    "HybridFunctor",
]


import functools
from collections.abc import Callable
from typing import Any, Concatenate, NoReturn, TypeGuard, overload

from ...brick.field._strategy import morphing, strategy
from ...port import functorial
from ...port.link import portlink
from ._tor import BaseFunctor


@portlink(functorial.HybridFunctorial)
class HybridFunctor[In, Out, **P](BaseFunctor[Concatenate[In, P], Out]):
    """Extend Call for Hybrid3 and use Init for Hybrid2"""

    def __init__(self, detect: functorial.Detect[In] | None, **kwargs):
        if detect is not None:
            setattr(self, "detect", detect)  # noqa:B010
        super().__init__(**kwargs)

    @strategy
    def detect(self, target: Any, /) -> TypeGuard[In]:
        """Check if target is direct function call"""
        raise NotImplementedError("typing.TypeGuard needed to detect!", target)

    @strategy
    def wrap[**Fn](
        self, fn: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]:
        """Case 2: Decorator"""

        @functools.wraps(fn)
        def wrapper(*fn_args: Fn.args, **fn_kwargs: Fn.kwargs) -> Out:
            return self.call(fn(*fn_args, **fn_kwargs), *args, **kwargs)

        return wrapper

    @morphing
    def bind[**Fn](
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[Fn, In]], Callable[Fn, Out]]:
        """Case 3: Bind additional input to case 2"""
        return lambda fn: self.wrap(fn, *args, **kwargs)

    def reject(self, failed: Any, *args, **kwargs) -> NoReturn:
        self.emit("Invalid Hybrid Usage", failed, *args, **kwargs)
        raise TypeError("Invalid Hybrid Usage")

    @overload
    def __call__(
        self, target: In, /, *args: P.args, **kwargs: P.kwargs
    ) -> Out: ...
    @overload
    def __call__[**Fn](
        self, target: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]: ...
    @overload
    def __call__(
        self, /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[..., In]], Callable[..., Out]]: ...

    def __call__(
        self, target: Any = None, /, *args: P.args, **kwargs: P.kwargs
    ):
        """Hybrid triple dispatch"""

        if self.detect(target):
            return self.call(target, *args, **kwargs)

        if callable(target) and target is not type:
            return self.wrap(target, *args, **kwargs)

        if target is None:
            return self.bind(*args, **kwargs)

        self.reject(target)
