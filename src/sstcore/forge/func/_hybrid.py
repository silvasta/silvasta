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

from ...brick.field import MorphingField, StrategyField
from ...port.functorial import BoundWrapper, Detect, HybridFunctorial
from ...port.link import portlink
from ._tor import BaseFunctor, FunctorInput


@portlink(HybridFunctorial)
class HybridFunctor[In, Out, **P](
    BaseFunctor[Concatenate[In, P], Out],
    data=FunctorInput,  # TODO: handle by Base!
):
    """Extend Call for Hybrid3 and use Init for Hybrid2"""

    def __init__(self, detect: Detect[In] | None = None, **kwargs) -> None:
        if detect is not None:  # LATER: FunctorInput(TypedDict) ??
            self._detect = detect
        super().__init__(**kwargs)

    @StrategyField(bind_to_self=True)
    def _detect(self, target: Any, /) -> TypeGuard[In]:
        """Check if target is direct function call"""
        raise NotImplementedError("typing.TypeGuard needed to detect!", target)

    @StrategyField(bind_to_self=True)
    def _wrap[**Fn](
        self, fn: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]:
        """Case 2: Decorator"""

        @functools.wraps(fn)
        def wrapper(*fn_args: Fn.args, **fn_kwargs: Fn.kwargs) -> Out:
            return self._call(fn(*fn_args, **fn_kwargs), *args, **kwargs)

        return wrapper

    @MorphingField(bind_to_self=True)
    def _bind(self, *args: P.args, **kwargs: P.kwargs) -> BoundWrapper[In, Out]:
        """Case 3: Bind additional input to case 2"""
        return lambda fn: self._wrap(fn, *args, **kwargs)

    def _reject(self, failed: Any, *args, **kwargs) -> NoReturn:
        raise TypeError("Invalid Hybrid Usage", failed, args, kwargs)

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
    ) -> BoundWrapper[In, Out]: ...

    def __call__(
        self, target: Any = None, /, *args: P.args, **kwargs: P.kwargs
    ):
        """Hybrid triple dispatch"""

        if self._detect(target):
            return self._call(target, *args, **kwargs)

        if callable(target) and target is not type:
            return self._wrap(target, *args, **kwargs)

        if target is None:
            return self._bind(*args, **kwargs)

        self._reject(target)
