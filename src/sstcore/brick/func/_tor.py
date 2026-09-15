"""
Prepare the Func/Obj

- Pick and provide the best of OOP/FP

"""

import sys
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    NoReturn,
    Protocol,
    TypeGuard,
    Unpack,
    cast,
    runtime_checkable,
    overload,
)

from loguru import logger

from ...port.functor import (
    DecoFunctorial,
    ErrorPolicy,
    Functor,
    HybridFunctorial1,
    HybridFunctorial2,
    HybridFunctorial3,
    HybridPolicy,
    SafeFunctorial,
)
from ..format import cls_name, reflect
from ..none import Ghost


class BaseFunctor[**Param, Result]:
    """Ensure Requirements and close MRO forwarding"""

    def __init__(
        self,
        func: Callable[Param, Result] | None = None,
        name: str = "",
        **kwargs,
    ):
        self._func: Callable[Param, Result] | None = func
        self._set_names(name)
        kwargs and self.emit("Unconsumed kwargs at BaseFunctor!", **kwargs)
        super().__init__()

    def _set_names(self, name: str):
        if not name:
            name = reflect.func(self._func, default=f"{cls_name(self)}Unit")
        self.__name__: str = name
        self.__qualname__: str = name

    def __call__(self, *args: Param.args, **kwargs: Param.kwargs) -> Result:
        if not self._func:
            raise NotImplementedError("Provide func or override __call__!")
        return self._func(*args, **kwargs)

    def emit(self, *args, **kwargs) -> None:  # LATER: override or inject?
        logger.debug(*args, **kwargs)


def test_func(argument: str, x: int = 3) -> int:
    print(f"{argument=}")
    return 2 * x


f1 = BaseFunctor(test_func, "double")
f2: BaseFunctor = BaseFunctor(test_func, "double")
f3: BaseFunctor[[str], int] = BaseFunctor(test_func, "double")
f4: BaseFunctor[[str, int], int] = BaseFunctor(test_func, "double")
# TEST: delete later


class TestExtendFunctor(BaseFunctor):
    pass


if TYPE_CHECKING:
    _instance: Functor = BaseFunctor()
    _class: type[Functor] = BaseFunctor
    _GhostFunctor = BaseFunctor
else:
    _GhostFunctor = Ghost

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Essentials
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class SafeFunctorMixin[**Param, Result]:
    # INFO: class SafeFunctorMixin[**Param, Result](_GhostFunctor):
    # -> causes ty confusion at:
    # class SafeFunctor[**P, R](SafeFunctorMixin[P, R], BaseFunctor[P, R]): ...
    # -> results in:
    # ├╴  Inconsistent type arguments for `BaseFunctor` among class bases ty (invalid-generic-class) [154, 7]
    __call__: Callable  # NOTE: toggle this while implementing

    def __init__(
        self,
        catch: Callable[[Exception, Any], Result | None] | None = None,
        error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE,
        exit_code: int = 1,
        **kwargs,
    ):
        self.catch: Callable[[Exception, Any], Result | None] | None = catch
        self.error_policy: ErrorPolicy = error_policy
        self.exit_code: int = exit_code
        super().__init__(**kwargs)

    def safe(
        self, *args: Param.args, **kwargs: Param.kwargs
    ) -> Result | None | NoReturn:
        """Execute Function in Safe Environment"""
        try:
            return self(*args, **kwargs)
        except Exception as error:
            if self.catch:
                return self.catch(error, *args, **kwargs)
            return self.on_error(error, *args, **kwargs)

    def result(
        self, *args: Param.args, **kwargs: Param.kwargs
    ) -> Result | NoReturn:
        """Provide Result or Raise on None"""
        if (result := self.safe(*args, **kwargs)) is None:
            raise RuntimeError("Nonething is impossible...")
        return result

    def on_error(self, error: Exception, *_, **__) -> Any | NoReturn:
        """Handle Function fail by Policy if Catch is not defined"""
        logger.critical(f"{self} failed: {error}")

        match self.error_policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                logger.error(f"Original error: {error}")
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise error


if TYPE_CHECKING:
    _instance: SafeFunctorial = SafeFunctorMixin()
    _class: type[SafeFunctorial] = SafeFunctorMixin


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Extensions
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class DecoFuncMixin[**Param, Result]:  # TODO:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class _DecoFunctor[**P, R](DecoFuncMixin[P, R], BaseFunctor[P, R]): ...


if TYPE_CHECKING:
    _instance: DecoFunctorial = DecoFuncMixin()
    _class: type[DecoFunctorial] = DecoFuncMixin


class SafeFunctor[**P, R](SafeFunctorMixin[P, R], BaseFunctor[P, R]): ...


#  TEST:  - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Detect[In](Protocol):
    def __call__(self, target: object) -> TypeGuard[In]: ...


class HybridFunctorMixin[In, Out, **P]:
    """Dispatch only. Logic lives in _func / apply."""

    _func: Callable[Concatenate[In, P], Out]
    detect: Detect[In]
    reject: Callable[[object], NoReturn]

    def apply(self, value: In, /, *args: P.args, **kwargs: P.kwargs) -> Out:
        return self._func(value, *args, **kwargs)

    def wrap[**Fn](
        self, fn: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]:
        @wraps(fn)
        def wrapper(*fn_args: Fn.args, **fn_kwargs: Fn.kwargs) -> Out:
            return self.apply(fn(*fn_args, **fn_kwargs), *args, **kwargs)

        return wrapper

    def delay(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[..., In]], Callable[..., Out]]:
        return lambda fn: self.wrap(fn, *args, **kwargs)

    def __call__(
        self,
        target: object = None,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> object:
        if self.detect(target):
            return self.apply(target, *args, **kwargs)
        if callable(target) and target is not type:
            return self.wrap(target, *args, **kwargs)
        if target is None:
            return self.delay(*args, **kwargs)
        self.reject(target)


if TYPE_CHECKING:
    _instance: HybridFunctorial1 = HybridFunctorMixin()
    _class: type[HybridFunctorial1] = HybridFunctorMixin
    # that below could be enough
    _instance: Functorial = HybridFunctorMixin()
    _class: type[Functorial] = HybridFunctorMixin


# AI_FOCUS: despite all the issues here, this looks overall like the best approach
# - as mentioned above, a shared base class is nice to share functionalities,
#   and to confirm this here, is not a requirement that must be fulfilled
# - still: the split must be clear and make sense, the special __call__ might be a reason
# - a minimal base could be useful just for the name and emit which are like highly desired
# Gather ideas how to decompose mixins in useful bricks and trees how to assemble them


class HybridFunctor1[In, Out, **P](
    HybridFunctorMixin[In, Out, P],
    BaseFunctor[Concatenate[In, P], Out],
):
    def __init__(
        self,
        func: Callable[Concatenate[In, P], Out],
        *,
        detect: Detect[In],
        reject: Callable[[object], NoReturn],
        name: str = "",
        **kwargs,
    ):
        self.detect = detect
        self.reject = reject
        super().__init__(func=func, name=name, **kwargs)


if TYPE_CHECKING:
    _unit = cast(HybridFunctor1, Any)
    _instance: HybridFunctorial1 = _unit
    _class: type[HybridFunctorial1] = HybridFunctor1

#  TEST:  - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
from typing import (  # noqa: E402
    Any,
    ParamSpec,
    Protocol,
    TypeVar,
)

P = ParamSpec("P")
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


@runtime_checkable
class InputDiscriminator(Protocol):
    def __call__(self, obj: Any) -> bool: ...


class HybridFunctor2[**P, InputT, OutputT](
    BaseFunctor[[InputT], OutputT],
    SafeFunctorMixin,
):
    """Reusable hybrid built on your Functor stack."""

    def __init__(
        self,
        logic: Callable[[InputT], OutputT],
        *,
        name: str = "",
        is_input: InputDiscriminator | None = None,
        converter: Callable[[Any], InputT] | None = None,
        **kwargs,
    ):
        super().__init__(func=logic, name=name or logic.__name__, **kwargs)
        self.logic = logic
        self.is_input = is_input or _as_path_input
        self.converter = converter  # e.g. PathSpec.ok

    def __call__(self, target: Any = None, /, **policy: Any) -> Any:
        effective_policy = {
            **self.__dict__.get("default_policy", {}),
            **policy,
        }

        if self.is_input(target):
            converted = self.converter(target) if self.converter else target
            return self.logic(
                converted, **effective_policy
            )  # or self.safe(...)

        if callable(target):
            return self._make_wrapper(target, **effective_policy)

        if target is None:

            def decorator(fn: Callable[P, InputT]) -> Callable[P, OutputT]:
                return self._make_wrapper(fn, **effective_policy)

            return decorator

        self.emit("Invalid usage", target=target, policy=effective_policy)
        raise PathGuardError(PathGuardReason.DECORATOR, target=target)

    def _make_wrapper(
        self, func: Callable[P, InputT], **policy: Any
    ) -> Callable[P, OutputT]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> OutputT:
            base = func(*args, **kwargs)
            converted = self.converter(base) if self.converter else base
            return self.logic(converted, **policy)  # or self.safe(...)

        return wrapper


if TYPE_CHECKING:
    _unit = cast(HybridFunctor2, Any)
    _instance: HybridFunctorial2 = _unit
    _class: type[HybridFunctorial2] = HybridFunctor2


#  TEST:  - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class HybridFunctor3[Target, **P, R]:
    def __init__(
        self,
        logic: Callable[..., R],
        is_target: Callable[[Any], TypeGuard[Target]],
        **default_policy: Unpack[HybridPolicy],
    ):
        self.logic = logic
        self.is_target = is_target
        self.default_policy = default_policy

    def __call__(
        self, target: Any = None, /, **policy: Unpack[HybridPolicy]
    ) -> Any:
        active_policy = {**self.default_policy, **policy}

        # Case 1: Direct Execution (Data provided)
        if self.is_target(target):
            return self.logic(target, **active_policy)

        # Case 2: Bare Decorator (Function provided)
        if callable(target):
            fn = target

            @wraps(fn)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                # Execute the wrapped function to get the Target, then apply logic
                return self.logic(fn(*args, **kwargs), **active_policy)

            return wrapper

        # Case 3: Parameterized Decorator (None provided, kwargs set)
        if target is None:

            def decorator(fn: Callable[P, Target]) -> Callable[P, R]:
                return self(fn, **active_policy)  # recursive call to Case 2

            return decorator

        raise TypeError(
            f"Invalid target: expected {Target.__name__} or Callable, got {type(target)}"
        )


if TYPE_CHECKING:
    _unit = cast(HybridFunctor3, Any)
    _instance: HybridFunctorial3 = _unit
    _class: type[HybridFunctorial3] = HybridFunctor3


class FilePolicy(HybridPolicy):
    raise_error: bool
    default_content: str | None


# The discriminator replaces `_as_path_input`
def is_path_input(obj: Any) -> TypeGuard[PathInput]:
    return isinstance(obj, (Path, str, PathSpec))


# Instantiate the Functor
ensure_file: HybridFunctorial3 = HybridFunctor3[PathInput, ..., Path](
    logic=_ensure._ensure_file_logic,
    is_target=is_path_input,
    raise_error=True,
    default_content=None,
)

ensure_file(
    # AI: the line below is showed in the type checker hint...
    # self, target: Any = None, /, **policy: object
    # - something like this is not acceptable
)
