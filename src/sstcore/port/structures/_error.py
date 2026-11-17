"""
Define the lowest level of custom Errors

-
"""

__all__: list[str] = [
    "ErrorClsField",
]

import sys
from collections.abc import Callable, Iterator
from functools import partial
from types import FrameType
from typing import Any

from rich import print
from rich.panel import Panel

from .._error import SstError
from .._types import _LockedClsMeta
from ._primitives import Var


def _caller_context(depth: int = 2) -> str:
    # EXTRACT: random drop from port.structures.__errror
    """Detect caller Class.method or function name from stack frame"""
    try:
        frame: FrameType = sys._getframe(depth)
        func_name: str = frame.f_code.co_name
        if "self" in frame.f_locals:
            cls_name: str = type(frame.f_locals["self"]).__name__
            return f"{cls_name}.{func_name}"
        if "cls" in frame.f_locals and isinstance(frame.f_locals["cls"], type):
            cls_name: str = frame.f_locals["cls"].__name__
            return f"{cls_name}.{func_name}"
        return func_name
    except ValueError:
        return "Unknown"  # CHECK: "" or VOID, let caller decide?


class GateRaiserMeta(_LockedClsMeta, type):
    """Equip Raiser classes with iteration and error formatting"""

    _name: str = "Error"

    def _meta_and_cls_attrs(cls) -> dict[str, Any]:
        return {**type(cls).__dict__, **cls.__dict__}

    def __iter__(cls) -> Iterator[Var]:
        for name in cls._meta_and_cls_attrs():
            if not name.startswith("_"):
                yield Var.gettr(cls, name)


type Errors = tuple[type[SstError], type[Exception]]


def _weave_sst_error[E: Exception](error: type[E]) -> type[SstError]:  # ty:ignore
    """Mix SstError with BuiltIn Exception"""

    if issubclass(error, SstError):
        return error

    bases: Errors = (SstError, error)
    name = f"{bases[0].__name__[0:-5]}{bases[-1].__name__}"

    return type(name, bases, {})


class ErrorClsField[**P]:  # AI: does this work on not Cls as well?
    """Wire error name, owner class, and provide message template"""

    def __new__[E: Exception](
        cls,
        error_type: type[E],
        template: str,
        /,
        *,
        preprocess: Callable[..., tuple[tuple[Any, ...], dict[str, Any]]]
        | None = None,
    ) -> Callable[P, SstError]:
        # NEXT: wire this proper, or does it already work? at least not-used args should be silenced
        return super().__new__(cls)

    def __init__[E: Exception](
        self,
        error_type: type[E],
        template: str,
        /,
        *,
        preprocess: Callable[..., tuple[tuple[Any, ...], dict[str, Any]]]
        | None = None,
        caller_depth: int = 2,
    ):
        self.error_type: type[E] = _weave_sst_error(error_type)
        self.template: str = template
        self.preprocess = preprocess
        self.name: str = ""
        self.caller_depth: int = caller_depth

    def __call__(self, *args, **kwargs):
        # AI_TASK: here is the place where the field will be possible
        pass

    def __set_name__(self, owner: type, name: str) -> None:
        # AI: why not just take the owner here??
        self.owner = owner
        self.name = name

    def __str__(self):
        return f"{self.owner.__name__}.{self.name}"

    def _build(self, owner: type, /, *args: Any, **kwargs: Any):
        """Format payload from positional/keyword args if provided"""

        if self.preprocess is not None:
            args, kwargs = self.preprocess(*args, **kwargs)

        text: str = (
            self.template.format(*args, **kwargs)
            if (args or kwargs)
            else self.template.format(
                *([""] * 5)  # AI: why does this make sense?
            )
        )
        caller: str = _caller_context(self.caller_depth)

        message = f"{caller}[{self}] {text}"

        return self.error_type(message.strip())

    def __get__(self, _unit: Any, owner: type) -> Callable[P, SstError]:
        # CHECK:
        # target_cls: type = instance if isinstance(instance, type) else owner
        return partial(self._build, owner)


class CustomErrorDescriptor[**P, E: Exception]:
    """Wraps a custom method so it gets the same caller/owner prefixing as ErrorPresetField."""

    # AI: unsure about this, maybe just use ErrorClsField.__call__ and set ErrorClsField.preprocess=func

    def __init__(self, func: Callable[P, E]) -> None:
        self.func = func
        self.name: str = getattr(func, "__name__", "CannotIdendifyFunc")

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def _invoke(self, owner: type, /, *args: P.args, **kwargs: P.kwargs) -> E:
        exc: E = self.func(*args, **kwargs)
        _owner: str = owner.__name__

        error: str = getattr(exc, "__name__", "NONE")
        message = f"[{_owner}.{error}]"
        exc.args = (f"{message} {exc}", *exc.args[1:])
        return exc

    def __get__(self, instance: Any, owner: type) -> Callable[P, E]:
        return partial(self._invoke, owner)


class GateRaiser(metaclass=GateRaiserMeta):
    """Explain Failures Meaningful"""

    cache1 = ErrorClsField[[str]](
        KeyError,
        "Cache miss for lookup key {0!r}",
    )

    out_of_range = ErrorClsField[[str, int]](
        ValueError,
        "Field {0} exceeded max limit {1}",
    )
    not_initialized = ErrorClsField[[]](
        RuntimeError,
        "System is not initialized",
    )

    @CustomErrorDescriptor
    def invalid_type_deco(expected: type, actual: Any, /):  # noqa:N805
        return TypeError(
            f"Expected {expected.__name__}, got {actual!r} ({type(actual).__name__})"
        )

    @ErrorClsField(TypeError, "Expected {0}, got {1} ({2}")
    def deco1(expected: type, actual: Any, /):  # noqa:N805
        # IDEA: 1 - as preprocess
        return expected.__name__, actual, type(actual).__name__

    @ErrorClsField(TypeError, "")
    def deco2(expected: type, actual: Any, /):  # noqa:N805
        # IDEA: 2 - as custom format
        return f"Expected {expected.__name__}, got {actual!r} ({type(actual).__name__})"


if __name__ == "__main__":
    print(GateRaiser.cache1("works"))
    print(GateRaiser.out_of_range("hello", 1))
    print(GateRaiser.not_initialized())

    print(GateRaiser.invalid_type_deco(Var, "hello"))

    def _panel(text, style="cyan", /):
        print(Panel(text, style=style))

    for attr in GateRaiser:
        try:
            _panel(f"{attr}")
            print(task := attr("hello"))

            if isinstance(task, BaseException):
                _panel("RAISE", "bold white on purple3")
                raise task
            else:
                _panel(f"Nothing to raise: {task}", "green")
        except Exception as error:
            _panel(f"Error: {task}", "red")
            print(f"{error}")
            print(f"{error=}")
            print(error)
        finally:
            print("--- " * 5)

    print(f"{GateRaiser.cache1("loader is missing")=}")
