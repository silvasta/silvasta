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


from collections.abc import Callable
from functools import cached_property, partial
from inspect import cleandoc
from typing import TYPE_CHECKING, Any, Literal, Self

from .._raise import LinkRaiser
from ..raising import SstCoreError
from ._define import (
    Collecting,
    Detecting,
    Doc,
    Docs,
    DunderSet,
    DunderStore,
    PlugDoc,
    PortDoc,
    PortLinkCollect,
    Projecting,
    Redacting,
    SidePolicy,
)
from ._render import _load_printer

if TYPE_CHECKING:
    from ._control import LinkConfig


class EasyNote:
    """Stable Base for all Easy Member"""

    spec: LinkConfig

    def emit(self, *args, **kwargs):
        self.spec.emit(*args, sender=self, **kwargs)

    def __str__(self):
        return f"{type(self).__name__}"


class EasyCore[Core: Callable](EasyNote):  # TODO: resolve wiring
    """Stable Core for all Easy Member"""

    core: Core
    __core__: Core

    def __call__(self, *args, **kwargs):
        return (
            self.core(*args, **kwargs)
            if hasattr(self, "core")
            else self.__core__(*args, **kwargs)
        )


class EasyCatch(EasyCore):
    def __core__(self, *args, **kwargs):  # TODO: sync with strategy!
        with self:
            super().__core__(*args, **kwargs)

    def __enter__(self) -> Self:
        self.emit(f"{self}: Executing Pipeline in Context")
        return self

    def __exit__(self, _error_type, error, _traceback):
        self.emit(f"{self}: Closing context")

        if _error_type is None:
            self.emit(f"{self}: No Issues...")
            return True

        self.emit(f"{self}: {(name := _error_type.__name__)}")

        if isinstance(error, SstCoreError):
            self.emit(f"Critical! {name=}")
            return True

        if isinstance(error, (AttributeError, TypeError)):
            self.emit(f"Continue... {name=}")
            return True

        return True  # NEXT:


REFLECT: frozenset[str] = frozenset(
    {
        "detect",
        "collect",
        "project",
        "redact",
    }
)


class Reflector[Core: Callable](EasyCatch):
    """Mixed Base for all Easy Member"""

    _registry: dict[str, type[Self]] = {}

    def __init__(self, spec: LinkConfig):
        if missing := REFLECT - (registry := self._registry.keys()):
            raise RuntimeError(f"Missing Operators! [{missing}]({registry=})")

        self.spec: LinkConfig = spec

    def __init_subclass__(cls, id: str, **kwargs):
        super().__init_subclass__(**kwargs)
        if id in cls._registry:
            raise LinkRaiser.PipeLine(
                f"Duplicated {cls}[{id}]", id=id, state=cls._registry
            )
        else:
            cls._registry[id] = cls

    # IMPORTANT: provide cached instances! 4 inits per decorated, 2 of it in loop!
    # - find mechanism and rule when to reset and rebuild, somewhere __enter__ and __exit__

    @property
    def detect(self) -> type[Detector]:
        return self._registry["detect"]  # ty:ignore

    @property
    def collect(self) -> type[Collector]:
        return self._registry["collect"]  # ty:ignore

    @property
    def project(self) -> type[Projector]:
        return self._registry["project"]  # ty:ignore

    @property
    def redact(self) -> type[Redactor]:
        return self._registry["redact"]  # ty:ignore


class EasyAccess:
    """Dot Access on all Dunders"""

    Dunders: type[DunderStore] = DunderSet
    dunders: set[str] = {  # MOVE: default, how to update?
        "__doc__",
        "__func__",
        "__links__",  # FIX:
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
            # FIX: invoke? and outsource to DunderSet
            return partial(self.invoke, attribute=method)
        raise LinkRaiser.PipeLine(f"__getattr__: {name}", state=self._methods)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# LATER: shared base of Inject/Reflect


class Operator[Core: Callable](EasyAccess, Reflector, id="base"):
    """Provide extended access for presets"""

    mode: Literal["soft", "hard"] = "soft"

    def __core__(self, target: Any, value: Any, attr: str):
        # NEXT: safe??
        _target = self.resolve(target, attr)
        self.strategy(_target, value, attr)

    @property
    def strategy(self) -> Core:  # NEXT: or what fits?
        match self.mode:
            case "soft":
                return self.polite
            case "hard":
                return self.direct

    def direct(self, *args, **kwargs):
        raise NotImplementedError

    def polite(self, *args, **kwargs):
        raise NotImplementedError

    def resolve(self, target: Any, attr: str) -> Any:
        raise NotImplementedError


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Projector(Operator[Projecting], id="inject"):
    """Collect the Modificating Methods with Safety"""

    __call__: Projecting

    # def __core__(self, target: Any, value: Any, attr: str):
    #     _target = self.resolve(target, attr)
    #     self.strategy(_target, value, attr)

    # @property
    # def strategy(self) -> Projector:
    #     match self.mode:
    #         case "soft":
    #             return self.polite
    #         case "hard":
    #             return self.direct

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


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Detector(Operator[Detecting], id="reflect"):
    """Collect the Detecting and Extracting Methods"""

    __call__: Reflector
    # mode: Literal["soft", "hard"] = "soft"  # IDEA: combine with inject?

    def __core__(self, target: type, attr: str, /):
        _target = self.resolve(target, attr)
        self.strategy(target, attr)

    # @property
    # def strategy(self) -> Reflector:  # IDEA: combine with inject? in EasyCore
    #     match self.mode:
    #         case "soft":
    #             return self.polite
    #         case "hard":
    #             return self.direct

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
        # NEXT: check dispatch: easy/soft? maybe remove
        raw: Any | None = (
            self.polite(target, "__doc__")
            if name
            else self.direct(target, "__doc__")
        )
        return self.clean(raw)

    def clean(self, doc: str | Any, /):
        return cleandoc(doc) if isinstance(doc, str) and doc else ""


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Collector(Reflector[Collecting], id="collect"):
    """Run the MRO pipelines and Reflect and Inject data"""

    __call__: Collecting
    nearest_target: type | None = None

    def __core__(
        self, port: type, plug: type, attr: str, /
    ) -> PortLinkCollect:
        data = PortLinkCollect()
        self.walk_mro(data, attr, cls=plug, side=SidePolicy.PLUG, nearest=True)
        if self.nearest_target is None:
            self.emit(f"Missing ancestor {plug.__name__} for {attr=}")
            # IDEA: let it continue, and see what DocMerger prints
        self.walk_mro(data, attr, cls=port, side=SidePolicy.PORT)
        self.emit(f"Extracted __doc__: {len(data)}")
        return data

    def walk_mro(
        self,
        data: PortLinkCollect,
        attr: str,
        *,
        cls: type,
        side: SidePolicy,
        nearest=False,
    ) -> None:
        for base in cls.__mro__:
            if self.spec.ignores(base):
                continue
            text: str = self.detect().doc(base, "")  # FIX:
            if text and (attr, base) not in data:
                if nearest and side == SidePolicy.PLUG:
                    self.nearest_target: type = base
                    nearest = False
                data.fill(side.retrieve(text, attr, source=base))


class Redactor(Reflector, id="redact"):
    __call__: Redacting  # NEXT:

    def __call__(self, docs: Docs, spec: LinkConfig | None = None) -> str:

        # NEXT: something like this:
        _spec_to_emit_and_format: LinkConfig = spec or LinkConfig()  # FIX:
        port: list[Doc] = []
        plug: list[Doc] = []
        fail: list[Doc] = []
        self.printer = _load_printer()  # NEXT: this must come from config, either the func or the flag/command
        for doc in docs:
            self.printer.line(color="cyan")
            match doc:  # MOVE: side policy! fill all 3 lists in 1 call
                case PortDoc():
                    self.sort_for_port(doc, port, fail)
                case PlugDoc():
                    self.sort_for_plug(doc, plug, fail)
        self.handle_sort(port, plug, fail)
        lines: list[str] = self.schema1(port, plug)
        return "\n".join(lines)

    def schema1(self, port: list[Doc], plug: list[Doc]) -> list[str]:
        lines: list[str] = []
        if port:
            first, *remaining = port
            self.format_port_header(first, lines)
            self.format_port_body(remaining, lines)
        if plug:
            self.format_separator(lines)
            self.format_plug_body(plug, lines)
        self.printer.panel(f"Statsistic: Total (multi) lines: {len(lines)}")
        return lines

    def format_port_header(self, first: Doc, lines: list[str]):
        lines.append(first.text.strip("\n"))
        self.printer(f"Attached Port header: {first.key}")

    def format_port_body(self, remaining: list[Doc], lines: list[str]):
        for doc in remaining:
            lines.append("\n")
            attr_draw: str = f".{doc.attr}" if doc.attr else ""
            lines.append(f"[{doc.source.__name__}{attr_draw}]")
            lines.append(doc.text.strip("\n"))

    def format_separator(self, lines):
        lines.append("\n\n", "--- -- ---" * 8, "\n\n", "Implementation", "\n")

    def format_plug_body(self, plug: list[Doc], lines: list[str]):
        for doc in plug[::-1]:  # CHECK: reverse
            lines.append("\n")
            attr_draw: str = f".{doc.attr}" if doc.attr else ""
            lines.append(f"[{{{doc.source.__name__}}}{attr_draw}]")
            lines.append(doc.text.strip("\n"))

    def handle_sort(self, port: list[Doc], plug: list[Doc], fail: list[Doc]):
        self.printer.panel(
            f"Stats: port: {len(port)}, plug: {len(plug)}, fail: {len(fail)} "
        )
        if not plug:
            self.printer.panel(
                "Implementation", frame="yellow", title="Missing"
            )
        if not port:
            self.printer.panel("Definitions", frame="orange", title="Missing")
        if fail:
            self.printer.panel(*fail, frame="red", title="Failed")

    def sort_for_port(self, doc: Doc, port: list, fail: list) -> None:
        if SidePolicy.PORT.validate(doc):
            port.append(doc)
            self.printer(f"Accepted: {doc.key}")
        else:
            fail.append(doc)
            self.printer(f"Rejected: {doc.key}")

    def sort_for_plug(self, doc: Doc, plug: list, fail: list) -> None:
        if SidePolicy.PLUG.validate(doc):
            plug.append(doc)
            self.printer(f"Accepted: {doc.key}")
        else:
            fail.append(doc)
            self.printer(f"Rejected: {doc.key}")
