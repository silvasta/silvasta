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
from typing import Any, Literal, NamedTuple, Self

from .._raise import LinkRaiser
from ..empty import VOID, MayBe
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

    __core__: Core

    def __call__(self, *args, **kwargs):
        return self.__core__(*args, **kwargs)


class Param(NamedTuple):
    """Track the ongoing Actions"""

    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __str__(self):
        return f"args={self.args}, kwargs={self.kwargs}"

    def __repr__(self):
        return str(self)  # LATER: explain each (kw)arg


class EasyCatch(EasyCore):
    """Execute in Context and Safe reflecting Operations"""

    _last_call: MayBe[Param] = VOID

    def __call__(self, *args, **kwargs):
        self._last_call = Param(args, kwargs)
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
        if self._last_call is not VOID:
            self.emit(f"Call context: {self._last_call}")
            self._last_call: VOID = VOID

        if isinstance(error, SstCoreError):
            self.emit(f"Specific: {error=}")
            return False

        if isinstance(error, (AttributeError, TypeError)):
            self.emit(f"Continue: {error=}")
            return type(self) is Reflector

        return False


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

    def invoke(self, target: Any, *args: Any, method: str) -> Any:
        """Uniform hook for dunder shortcut calls (e.g. op.doc(target, ...))."""
        return self(target, method, *args)

    def __getattr__(self, name: str) -> Callable:
        if name.startswith("_"):
            raise AttributeError(name)
        self.emit(f"[{self}].__getattr__: {name}")
        if method := self._methods.get(name):
            return partial(self.invoke, method=method)
        raise AttributeError(f"'{self}' object has no attribute '{name}'")


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Operator[Core: Callable](EasyAccess, Reflector, id="base"):
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
            self.mode: Literal["soft", "hard"] = prev

    @property
    def strategy(self):  # NEXT: what type fits?
        match self.mode:
            case "soft":
                return self.polite
            case "hard":
                return self.direct

    def __core__(self, target: Any, attr: str, *args: Any) -> Any:
        if (resolved := self.pre(target, attr)) is None:
            return None
        result = self.strategy(resolved, attr, *args)
        return self.post(result, attr)

    def pre(self, target: Any, attr: str, /) -> Any:
        """Unwrap descriptors when reading or writing __doc__s"""
        if attr == "__doc__":
            if isinstance(target, property):
                return target.fget
            if isinstance(target, cached_property):
                return target.func
            if hasattr(target, "__func__"):
                return target.__func__
        return target

    def post(self, result: Any, attr: str, /) -> Any:
        """Hook for post-processing the strategy result."""
        return result

    def direct(self, *args, **kwargs):
        raise NotImplementedError(args, kwargs)

    def polite(self, *args, **kwargs):
        raise NotImplementedError(args, kwargs)

    def resolve(self, target: Any, attr: str, /) -> Any:
        return self.pre(target, attr)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Projector(Operator[Projecting], id="project"):
    """Collect the Modificating Methods with Safety"""

    __call__: Projecting

    def direct(self, target: Any, attr: str, value: Any, /) -> None:
        object.__setattr__(target, attr, value)

    def polite(self, target: Any, attr: str, value: Any, /) -> None:
        setattr(target, attr, value)


class Detector(Operator[Detecting], id="detect"):
    """Collect the Detecting and Extracting Methods"""

    __call__: Reflector

    def direct(self, target: Any, attr: str, /) -> Any:
        return getattr(target, "__dict__", {}).get(attr)

    def polite(self, target: Any, attr: str, /, default: Any = None) -> Any:
        return getattr(target, attr, default)

    def post(self, result: Any, attr: str, /) -> Any:
        if attr == "__doc__":
            return self.clean(result)
        return result

    def resolve(self, cls: type, attr: str, /) -> Any:
        """Resolve Class or its Member during MRO walk"""
        if not attr:
            return cls
        with self.on("hard"):
            raw: Any = self(cls, attr)
        match raw:
            case classmethod() | staticmethod():
                return raw.__func__
            case property() | cached_property():
                return raw
            case _ if callable(raw):
                return raw
            case _:
                return None

    def clean(self, doc: str | Any, /) -> str:
        return cleandoc(doc) if isinstance(doc, str) and doc else ""


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Collector(Reflector[Collecting], id="collect"):
    """Run the MRO pipelines and Reflect and Inject data"""

    __call__: Collecting
    nearest_target: type | None = None

    def __core__(self, port: type, plug: type, attr: str, /) -> PortLinkCollect:
        self.nearest_target = None
        data = PortLinkCollect()
        self.walk_mro(data, attr, SidePolicy.PLUG, plug, track_nearest=True)
        if self.nearest_target is None:
            self.emit(f"Missing implementation for {plug.__name__} and {attr=}")
        self.walk_mro(data, attr, SidePolicy.PORT, port, track_nearest=False)
        return data

    def stream(self, cls: type) -> Iterator[type]:
        """Yield filtered MRO bases of Cls"""
        for base in cls.__mro__:
            if not self.spec.ignores(base):
                yield base

    def walk_mro(
        self,
        data: PortLinkCollect,
        attr: str,
        side: SidePolicy,
        /,
        cls: type,
        *,
        track_nearest: bool = False,
    ) -> None:
        for base in self.stream(cls):
            if (target := self.detector.resolve(base, attr)) is None:
                continue

            if track_nearest and self.nearest_target is None:
                self.nearest_target: Any = target

            with self.detector.on("hard") as detect:
                text: str = detect.doc(target)

            if text and (attr, base) not in data:
                data.fill(side.ctor(text, attr, source=base))


class Redactor(Reflector, id="redact"):
    __call__: Redacting

    def __call__(self, docs: Docs, /) -> str:
        sorted: SortedDocs = SidePolicy.sort(docs)
        self.spec.show_result(sorted)
        lines: list[str] = schema1(*sorted.port_and_plug())
        # LATER: show_merge_result(...)
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
        lines.extend(["\n\n", "--- -- ---" * 8, "\n\n", "Implementation", "\n"])

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
