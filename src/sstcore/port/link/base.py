"""
Operators - the Base

- temporary module
"""

import functools as _f
import typing as _t
from types import SimpleNamespace

from ..raising import SstCoreError
from ._dunder import DunderSet, DunderStore
from ._printer import printer
from .define import PortEmit


class EasyBase(SimpleNamespace):  # CHECK: __init_subclass__ still from here?
    """Stable Base for all Easy Member"""

    _emit: _t.Callable | None = None

    def emit(self, *args, **kwargs):
        (self._emit or self._emit_default)(*args, **kwargs)

    @staticmethod
    def _emit_default(*args, **kwargs):
        print(*args, **kwargs)  # PARAM: debug toggle
        pass

    def __str__(self):
        todo = "TODO"
        return f"{type(self).__name__}[{todo}]"


class EasyCatchL1:
    emit: PortEmit

    def dispatch(self, *args, **kwargs):
        # TASK: sync with strategy!
        with self:
            return super().dispatch(*args, **kwargs)

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


class EasyCoreL1[Core: _t.Callable]:
    """Stable Core for all Easy Member"""

    # TASK: absorb strategy!
    core: Core
    # TODO:
    __core__: Core

    def __call__(self, *args, **kwargs):
        return (
            self.core(*args, **kwargs)
            if hasattr(self, "core")
            else self.__core__(*args, **kwargs)
        )


class EasyAccessL1:
    """Dot Access on all Dunders"""

    Dunders: type[DunderStore] = DunderSet
    dunders: set[str] = {
        "__doc__",
        "__func__",
        "__links__",
    }
    _methods: DunderStore

    def __init__(self, dunders: set[str] | None = None, **kwargs):
        self.dunders: set[str] = (dunders or set()) | self.dunders
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == "dunders":
            self._methods: DunderStore = self.Dunders(self.dunders)

    # AI: bound type for Callable possible?
    def __getattr__(self, name: str) -> _t.Callable:
        self.emit(f"[{self}].__getattr__: {name}")  # REMOVE: after debug
        if method := self._methods.get(name):
            return _f.partial(self.invoke, attribute=method)
        raise AttributeError(f"Fail in __getattr__: {name}", self._methods)


#  LINE: -- Testing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def test_access():
    with printer.topic("Easy1"):
        access1 = EasyAccessL1()
        printer(vars(access1))

    with printer.topic("Easy2"):
        access2 = EasyAccessL1({"test", "__cli_", "__log__"})
        printer(vars(access2))
        updates: set[str] = {"__port_doc__", "__rich__", "__portlinkdocs__"}
        access2.dunders = updates
        printer.header("Easy2 modified")
        printer(vars(access2))


if __name__ == "__main__":
    test_access()
