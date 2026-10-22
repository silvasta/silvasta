"""
Create the SimpleNamespace Easy Operators

- The massively over engineered backbone of the execution pipeline
- As well a collection of interesting ideas and sharp programming

- Redactor: The Docstring Merging Render Engine

                               DependencyLevel.sstcore.port.link[1]
"""

# TASK: raiser! or just import SstCoreError -> LinkError and export this to Raiser

__all__: list[str] = [
    "EasyNote",
    "EasyCore",
    "EasyCatch",
    "Reflector",
    "EasyAccess",
    "Operator",
    "Detector",
    "Projector",
    "Collector",
    "Redactor",
]


from collections.abc import Callable, Generator, Iterator
from contextlib import contextmanager
from functools import cached_property, partial
from inspect import cleandoc
from typing import Any, Literal, Self

from .._raise import LinkRaiser
from ..raising import SstCoreError
from ._define import (
    Collecting,
    Detecting,
    Docs,
    DunderSet,
    DunderStore,
    LinkConfig,
    PlugDocs,
    PortDoc,
    PortDocs,
    PortLinkCollect,
    Projecting,
    Redacting,
    SidePolicy,
    SortedDocs,
)


class EasyNote:
    """Stable Base for all Easy Member"""

    spec: LinkConfig

    def emit(self, *args, **kwargs):
        self.spec.emit(*args, sender=self, **kwargs)

    def __str__(self):
        return f"{type(self).__name__}"


class EasyCore[Core: Callable](EasyNote):  # TODO: resolve wiring
    """Stable Core for all Easy Member"""

    # core: Core
    __core__: Core

    def __call__(self, *args, **kwargs):
        return (  # TODO: clean up
            # self.core(*args, **kwargs)
            # if hasattr(self, "core")
            # else
            self.__core__(*args, **kwargs)
        )


class EasyCatch(EasyCore):
    def __call__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        with self:
            return super().__call__(*args, **kwargs)

    def __enter__(self) -> Self:
        self.emit(f"{self}: Executing Pipeline in Context")
        return self

    def __exit__(self, _error_type, error, _traceback):
        self.emit(f"{self}: Closing context")

        if _error_type is None:
            self.emit(f"{self}: No Issues...")
            return True

        self.emit(f"{self!r}: {error=}")
        if hasattr(self, "_args"):
            self.emit(*self._args)
        if hasattr(self, "_kwargs"):
            self.emit(*self._kwargs)

        if isinstance(error, SstCoreError):
            self.emit(f"Specific: {error=}")
            return False

        if isinstance(error, (AttributeError, TypeError)):
            self.emit(f"Continue: {error=}")
            return True

        return True


REFLECT: frozenset[str] = frozenset(("detect", "collect", "project", "redact"))


class Reflector[Core: Callable](EasyCatch):
    """Mixed Base for all Easy Member"""

    _registry: dict[str, type[Self]] = {}

    def __init__(self, spec: LinkConfig):
        if missing := REFLECT - (registry := self._registry.keys()):
            raise RuntimeError(f"Missing Operators! [{missing}]({registry=})")

        self.spec: LinkConfig = spec
        self._instances: dict[str, Self] = {}

    def __init_subclass__(cls, id: str, **kwargs):
        super().__init_subclass__(**kwargs)
        if id in cls._registry:
            raise LinkRaiser.PipeLine(
                f"Duplicated {cls}[{id}]", id=id, state=cls._registry
            )
        else:
            cls._registry[id] = cls

    def _get_op(self, key: str, /) -> Any:
        if key not in self._instances:
            self._instances[key] = self._registry[key](self.spec)
        return self._instances[key]

    @property
    def detector(self) -> Detector:
        return self._get_op("detect")

    @property
    def collector(self) -> Collector:
        return self._get_op("collect")

    @property
    def projector(self) -> Projector:
        return self._get_op("project")

    @property
    def redactor(self) -> Redactor:
        return self._get_op("redact")


class EasyAccess(Reflector, id="get"):
    """Dot Access on all Dunders"""

    Dunders: type[DunderStore] = DunderSet
    _methods: DunderStore

    def __init__(self, spec: LinkConfig, **kwargs: Any):
        super().__init__(spec, **kwargs)
        self._methods: DunderStore = self.Dunders(spec.dunders)

    def __getattr__(self, name: str) -> Callable:
        self.emit(f"[{self}].__getattr__: {name}")
        if method := self._methods.get(name):
            # FIX:
            # FIX:
            # FIX:
            # FIX:
            return partial(self.invoke, method=method)
        raise AttributeError


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Operator[Core: Callable](
    EasyAccess,
    Reflector,
    id="base",
):
    """Provide extended access for presets"""

    mode: Literal["soft", "hard"] = "soft"

    def __str__(self):
        return f"{type(self).__name__}[{self.mode}]"

    @contextmanager
    def on(self, mode: Literal["soft", "hard"] = "soft") -> Generator[Self]:
        """Temporarily switch operator mode ('soft' vs 'hard') inside a with-block."""
        prev, self.mode = self.mode, mode
        try:
            with self:
                yield self
        finally:
            self.mode = prev

    @property
    def strategy(self):  # NEXT: what type fits?
        match self.mode:
            case "soft":
                return self.polite
            case "hard":
                return self.direct

    def direct(self, *args, **kwargs):
        raise NotImplementedError(args, kwargs)

    def polite(self, *args, **kwargs):
        raise NotImplementedError(args, kwargs)

    def resolve(self, target: Any, attr: str, /) -> Any:
        raise NotImplementedError(target, attr)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Projector(Operator[Projecting], id="project"):
    """Collect the Modificating Methods with Safety"""

    __call__: Projecting

    def __core__(self, target: Any, attr: str, value: Any, /) -> None:
        resolved = self.resolve(target, attr)
        self.strategy(resolved, value, attr)

    def direct(self, target: Any, attr: str, value: Any, /):
        object.__setattr__(target, attr, value)

    def polite(self, target: Any, attr: str, value: Any, /):
        setattr(target, attr, value)

    def resolve(self, target: Any, attr: str, /) -> Any:
        if attr == "__doc__":
            if isinstance(target, property) and target.fget is not None:
                return target.fget
            if hasattr(target, "__func__"):
                return target.__func__
        return target

    def invoke(self, target, method, value) -> Any:
        return self(target, method, value)


class Detector(Operator[Detecting], id="detect"):
    """Collect the Detecting and Extracting Methods"""

    __call__: Reflector

    def __core__(self, target: Any, attr: str, /) -> Any:
        return self.strategy(target, attr)

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

    def doc(self, cls: Any, attr: str, /) -> str:
        """Resolve cls or cls.attr and return its cleaned docstring."""
        # AI: is this wired well?
        if (target := self.resolve(cls, attr)) is None:
            return ""
        with self.on(mode="soft" if attr else "hard"):
            doc: str | None = self(target, attr)
        return self.clean(doc)

    def clean(self, doc: str | Any, /):
        return cleandoc(doc) if isinstance(doc, str) and doc else ""

    def invoke(self, target, method) -> Any:
        return self(target, method)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Collector(Reflector[Collecting], id="collect"):
    """Run the MRO pipelines and Reflect and Inject data"""

    __call__: Collecting
    nearest_target: type | None = None

    def __core__(self, port: type, plug: type, attr: str, /) -> PortLinkCollect:
        self.nearest_target = None
        data = PortLinkCollect()
        self.walk_mro(
            data, attr, cls=plug, side=SidePolicy.PLUG, track_nearest=True
        )
        if self.nearest_target is None:
            self.emit(f"Missing implementation for {plug.__name__} and {attr=}")
        self.walk_mro(
            data, attr, cls=port, side=SidePolicy.PORT, track_nearest=False
        )
        return data

    def provide(self, cls: type) -> Iterator[type]:
        """Yield filtered MRO mases of Cls"""
        for base in cls.__mro__:
            if not self.spec.ignores(base):
                yield base

    def walk_mro(
        self,
        data: PortLinkCollect,
        attr: str,
        *,
        cls: type,
        side: SidePolicy,
        track_nearest: bool = False,
    ) -> None:
        for base in self.provide(cls):
            if (target := self.detector.resolve(base, attr)) is None:
                continue

            if track_nearest and self.nearest_target is None:
                self.nearest_target: Any = target

            text: str = self.detector.doc(base, attr)
            if text and (attr, base) not in data:
                data.fill(side.ctor(text, attr, source=base))


class Redactor(Reflector, id="redact"):
    __call__: Redacting

    def __call__(self, docs: Docs, /) -> str:
        sorted: SortedDocs = SidePolicy.sort(docs)
        self.spec.show_result(sorted)
        lines: list[str] = schema1(*sorted.port_and_plug())
        # TODO: show_merge_result(...)
        self.spec.printer.panel(f"Statsistic: Total Lines: {len(lines)}")
        return "\n".join(lines)


def schema1(port: PortDocs, plug: PlugDocs) -> list[str]:
    """Take Port- and Plug- Docs and Produce a Text"""

    def _format_port_header(first: PortDoc, lines: list[str]):
        lines.append(first.text.strip("\n"))

    def _format_port_body(remaining: PortDocs, lines: list[str]):
        for doc in remaining:
            lines.append("\n")
            attr_draw: str = f".{doc.attr}" if doc.attr else ""
            lines.append(f"[{doc.source.__name__}{attr_draw}]")
            lines.append(doc.text.strip("\n"))

    def _format_separator(lines):
        lines.append("\n\n", "--- -- ---" * 8, "\n\n", "Implementation", "\n")

    def _format_plug_body(plug: PlugDocs, lines: list[str]):
        for doc in plug[::-1]:  # CHECK: reverse
            lines.append("\n")
            attr_draw: str = f".{doc.attr}" if doc.attr else ""
            lines.append(f"[{{{doc.source.__name__}}}{attr_draw}]")
            lines.append(doc.text.strip("\n"))

    lines: list[str] = []

    if port:
        first, *remaining = port
        _format_port_header(first, lines)
        _format_port_body(remaining, lines)
    if port and plug:
        _format_separator(lines)
    if plug:
        _format_plug_body(plug, lines)

    return lines
