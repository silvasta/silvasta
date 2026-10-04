"""
Create the SimpleNamespace Easy Operators

- The massively over engineered backbone of the execution pipeline
- As well a collection of interesting ideas and sharp programming

                               DependencyLevel.sstcore.port.link[2]
"""

__all__: list[str] = [
    "EasyNote",
    "EasyCore",
    "EasyBase",
    "EasyCatch",
    "PortOperator",
    "Spawner",
    "EasyAccess",
    "Inject",
    "Reflect",
    "Collect",
]


from collections.abc import Callable
from functools import cached_property, partial
from inspect import cleandoc as _cleandoc
from types import SimpleNamespace
from typing import Any, Literal, Self

from .._raise import LinkRaiser
from ..raising import SstCoreError
from ._define import (
    Collecting,
    Injecting,
    LinkSpec,
    PortEmit,
    PortLinks,
    Reflecting,
)
from ._dunder import DunderSet, DunderStore
from ._model import SidePolicy


class EasyNote(SimpleNamespace):
    """Stable Base for all Easy Member"""

    _emit: Callable | None = None

    def emit(self, *args, **kwargs):  # TODO: check wiring
        (self._emit or self.port_emit)(*args, sender=self, **kwargs)

    @staticmethod
    def port_emit(*args, **kwargs):  # TODO: simple logger
        _sender = kwargs.pop("sender", None)
        print(f"{_sender=}", *args, **kwargs)  # PARAM: debug toggle
        pass

    def __str__(self):
        todo = "TODO"
        return f"{type(self).__name__}[{todo}]"


class EasyCore[Core: Callable](SimpleNamespace):
    # TODO: resolve wiring
    """Stable Core for all Easy Member"""

    core: Core
    __core__: Core

    def __call__(self, *args, **kwargs):
        return (
            self.core(*args, **kwargs)
            if hasattr(self, "core")
            else self.__core__(*args, **kwargs)
        )


class EasyBase[Core: Callable](EasyCore, EasyNote):
    """Mixed Base for all Easy Member"""

    _registry: dict[int, type[Self]] = {}

    def __init_subclass__(cls, id: int, art: str, **kwargs):
        super().__init_subclass__(**kwargs)
        if not id:
            cls.port_emit(f"{cls.__name__}: Ignored...")
        elif id in cls._registry:
            raise LinkRaiser.PipeLine(
                f"Duplicated {cls}[{id}]", id=id, state=cls._registry
            )
        else:
            cls._registry[id] = cls
            cls.port_emit(f"{cls.__name__}: Registered: {id}")


class EasyCatch(EasyBase, id=0, art="D"):
    emit: PortEmit

    def __core__(self, *args, **kwargs):  # TODO: sync with strategy!
        with self:
            super().__core__(*args, **kwargs)

    def __enter__(self) -> Self:
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
            return True

        if issubclass(exception_type, (AttributeError, TypeError)):
            self.emit(f"Continue... {exception_value=}")
            return True

        return True  # PARAM: Error Handling


class PortOperator[Core: Callable](EasyCatch, EasyBase, id=1, art="C"):
    """Mixed Base for all Easy Member"""

    @property
    def spawn(self) -> Spawner:
        return Spawner(registry=self._registry)


class Spawner:
    """Provide extended access for presets"""

    operators: frozenset[str] = frozenset({"reflect", "collect", "inject"})

    def __init__(self, registry: dict[int, Any]):
        if missing := self.operators - registry.keys():
            raise RuntimeError(f"Missing Operators! [{missing}]({registry=})")
        self._registry: dict[int, Any] = registry

    @property
    def inject(self) -> type[Inject]:
        return self._registry[3]

    @property
    def reflect(self) -> type[Reflect]:
        return self._registry[4]

    @property
    def collect(self) -> type[Collect]:
        return self._registry[5]


class EasyAccess(EasyBase, id=2, art="S"):
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

    def __getattr__(self, name: str) -> Callable:
        self.emit(f"[{self}].__getattr__: {name}")
        if method := self._methods.get(name):
            return partial(self.invoke, attribute=method)
        raise LinkRaiser.PipeLine(f"__getattr__: {name}", state=self._methods)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# LATER: shared base of Inject/Reflect


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Inject(PortOperator[Injecting], EasyAccess, id=3, art="O"):
    """Collect the Modificating Methods with Safety"""

    __call__: Injecting
    mode: Literal["soft", "hard"] = "soft"

    def __core__(self, target: Any, value: Any, attr: str):
        _target = self.resolve(target, attr)
        self.strategy(_target, value, attr)

    @property
    def strategy(self) -> Injecting:
        match self.mode:
            case "soft":
                return self.polite
            case "hard":
                return self.direct

    def direct(self, target: Any, value: Any, attr: str):
        object.__setattr__(target, attr, value)

    def polite(self, target: Any, value: Any, attr: str):
        setattr(target, attr, value)

    def resolve(self, target: Any, attr: str) -> Any:
        if attr == "__doc__":
            if isinstance(target, property) and target.fget is not None:
                return target.fget
            if hasattr(target, "__func__"):
                return target.__func__
        return target


def _inject_safe_example(target: Any, value: str, /, attr: str):
    with Inject(core=_inject_doc_raw) as injector:
        injector(target, attr, value)


def _inject_doc_raw(target: Any, value: str):
    object.__setattr__(target, "__doc__", value)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Reflect(PortOperator[Reflecting], EasyAccess, id=4, art="O"):
    """Collect the Detecting and Extracting Methods"""

    __call__: Reflecting
    mode: Literal["soft", "hard"] = "soft"  # IDEA: combine with inject?

    def __core__(self, target: type, attr: str, /):
        _target = self.resolve(target, attr)
        self.strategy(target, attr)

    @property
    def strategy(self) -> Reflecting:  # IDEA: combine with inject? in EasyCore
        match self.mode:
            case "soft":
                return self.polite
            case "hard":
                return self.direct

    def direct(self, target: type, attr: str, /):
        return target.__dict__.get(attr)

    def polite(self, target: type, attr: str, /, default=None):
        return getattr(target, attr, default)

    def resolve(self, cls: type, attr: str, /):
        match attr := self(cls, attr):
            case classmethod() | staticmethod():
                return attr.__func__
            case property() | cached_property():
                return attr
            case _ if callable(attr):
                return attr
            case _:
                return None

    def doc(self, target: Any, name: str, /) -> str:
        # IMPORTANT: check dispatch: easy/soft?
        raw: Any | None = (
            self.polite(target, "__doc__")
            if name
            else self.direct(target, "__doc__")
        )
        return self.clean(raw)

    def clean(self, doc: str | Any, /):
        return _cleandoc(doc) if isinstance(doc, str) and doc else ""


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Collect(PortOperator[Collecting], id=5, art="O"):
    """Run the MRO pipelines and Reflect and Inject data"""

    __call__: Collecting
    spec: LinkSpec  # IMPORTANT:
    nearest_target: type | None = None

    def __core__(self, port: type, plug: type, attr: str, /) -> PortLinks:
        data = PortLinks()
        self.walk_mro(data, attr, cls=plug, side=SidePolicy.PLUG, nearest=True)
        if self.nearest_target is None:
            self.emit(f"Missing ancestor {plug.__name__} for {attr=}")
            # IDEA: let it continure, and see what DocMerger prints
        self.walk_mro(data, attr, cls=port, side=SidePolicy.PORT)
        self.emit(f"Extracted __doc__: {len(data)}")
        return data

    def walk_mro(
        self,
        data: PortLinks,
        attr: str,
        *,
        cls: type,
        side: SidePolicy,
        nearest=False,
    ) -> None:
        for base in cls.__mro__:
            if self.spec.ignores(base):
                continue
            text: str = self.spawn.reflect().doc(base, "")
            if text and (attr, base) not in data:
                if nearest and side == SidePolicy.PLUG:
                    self.nearest_target: type = base
                    nearest = False
                data.fill(side.retrieve(text, attr, source=base))
