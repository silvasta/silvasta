"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

import functools
from collections.abc import Callable
from typing import (
    Any,
    Concatenate,
    NoReturn,
    Protocol,
    TypeGuard,
    overload,
)

from ...brick.field import (
    PolicyField,
    RequiredField,
)
from ...brick.field._strategy import morphing, strategy
from ...brick.labor import clsname, funcname
from ...port.functor import (
    ErrorPolicy,
    FuncEmit,
    Functor,
    HybridFunctorial,
    SafeFunctorial,
)
from ...port.link import portlink
from ..engine.blueprint import FunctorMeta, FunctorMetaData

FunctorInput = FunctorMetaData()


@portlink(Functor)
class BaseFunctor[**Args, Result](metaclass=FunctorMeta, data=FunctorInput):
    """Ensure Requirements and close MRO forwarding"""

    emit: FuncEmit

    def __init__(
        self,
        call: Callable[Args, Result] | None = None,
        name: str = "",
        **kwargs,
    ):
        if call:
            self.call: Callable[Args, Result] = call

        name: str = name or funcname(self.call, default=f"{clsname(self)}Unit")
        self.__name__: str = name
        self.__qualname__: str = name

        if kwargs:
            self.emit(f"Undestroyed kwargs: {kwargs!r}")

        super().__init__()

    def __call__(self, *args: Args.args, **kwargs: Args.kwargs) -> Result:
        return self.call(*args, **kwargs)


@portlink(SafeFunctorial)
class SafeFunctor[**Args, Result](BaseFunctor[Args, Result]):
    """Protect the Execution, Hanldle Errors, everything able to customize"""

    # AI: morphing
    catch: Callable[Concatenate[Exception, Args], Result | None]

    error_policy = PolicyField(ErrorPolicy.LOG_AND_CONTINUE)
    exit_code = RequiredField(types=int, default=1)

    def __init__(
        self,
        catch: Callable[[Exception, Any], Result | None] | None = None,
        **kwargs,
    ):
        if catch is not None:
            self.catch: Callable[[Exception, Any], Result | None] = catch
        super().__init__(**kwargs)

    def safe(
        self, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | None | NoReturn:
        """Execute Function in Safe Environment"""
        try:
            return self(*args, **kwargs)
        except Exception as error:
            self.catch(error, *args, **kwargs)


#  LINE: -- Hybrid -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Detect[In](Protocol):
    def __call__(self, target: Any) -> TypeGuard[In]: ...


@portlink(HybridFunctorial)
class HybridFunctor[In, Out, **P](BaseFunctor[Concatenate[In, P], Out]):
    detect: Detect[In]

    def __init__(self, detect: Detect[In] | None, **kwargs):
        if detect is not None:
            self.detect: Detect = detect
        super().__init__(**kwargs)

    def detect(self, target: Any, /) -> TypeGuard[In]:
        raise NotImplementedError("Need TypeGuard to detect!", target)

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
    def delay(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[..., In]], Callable[..., Out]]:
        """Case 3: Bind additional input to case 2"""
        return lambda fn: self.wrap(fn, *args, **kwargs)

    def reject(self, fail: Any, *args, **kwargs) -> NoReturn:
        # LATER: improve, use from ._hybrid
        self.emit("Invalid Hybrid Usage", fail, *args, **kwargs)
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
            return self.delay(*args, **kwargs)

        self.reject(target)
