"""
process

.
"""

import typing as _t
from collections.abc import Callable
from types import SimpleNamespace

from ..raising import SstCoreError
from .data import DocMerger


class EasyBase(SimpleNamespace):
    """Stable Base for all Easy Member"""

    _emit: Callable | None = None

    def emit(self, *args, **kwargs):
        (self._emit or self._emit_default)(*args, **kwargs)

    def _emit_default(self, *args, **kwargs):
        print(*args, **kwargs)


class EasyCatchL1(EasyBase):
    def __enter__(self) -> _t.Self:
        self.emit(f"{self}: Executing Pipeline in Context")
        return self

    def __exit__(self, exception_type, exception_value, _exception_trace_back):
        self.emit(f"{self}: Closing context")

        if exception_type is None:
            self.emit(f"{self}: No Issues...")
            return True

        self.emit(f"{self}: {(error := exception_type.__name__)}")

        if issubclass(exception_type, SstCoreError):
            self.emit(f"Critical! {error=}")
            return False

        if issubclass(exception_type, (AttributeError, TypeError)):
            self.emit(f"Continue... {exception_value=}")
            return True

        return True  # LATER: configured handling


class EasyCoreL1(EasyBase):
    """Stable Core for all Easy Member"""

    def __call__(self, *args, **kwargs):
        self.core(*args, **kwargs)


class Dunders(dict):
    def __init__(self, dunders: set[str]):
        """Assigning pairs of {target: __target__}"""
        for method in dunders:
            self[method.strip("_")] = f"__{method}__"


class EasyAccessL1(EasyBase):
    """Dot Access on all Dunders"""

    dunders: set[str] = {
        "__doc__",
        "__func__",
        "__links__",
    }
    targets: Dunders

    def __init__(self, dunders: set | None = None, **kwargs):
        self.dunders: set[str] = dunders or set()  # IDEA: |= to existin?
        self.targets = Dunders(self.dunders)  # LATER: automatic on change
        super().__init__(**kwargs)

    def __getattr__(self, name: str) -> _t.Any:
        if method := self.targets.get(name):  # TODO: wire
            self.emit(f"Access to Dunders: {method}")
            return self.invoke(method)
        raise AttributeError(f"Fail in __getattr__: {name}", self.dunders)

    def _invoke(self, *args, **kwargs):
        raise NotImplementedError(args, kwargs)

    def invoke(self, method: str):
        def wrapper(*args, **kwargs):
            self.emit(method, args, kwargs)
            self._invoke(method, *args, **kwargs)

        return wrapper


class InjectorBase[Core](EasyCatchL1, EasyCoreL1):
    __call__: Core


class CollectorBase[Core](EasyCatchL1):
    __call__: Core


class ReflectorBase[Core](EasyCoreL1):
    __call__: Core


class ProcessorBase[Core](EasyCoreL1):
    __call__: Core


#  LINE: -- Testing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def merger(source: str, target: str, /, joint: str = "") -> str:
    return f"""{source}{joint}{target}"""


proc: ProcessorBase[DocMerger] = ProcessorBase(state="running", core=merger)

c = proc((), ())
