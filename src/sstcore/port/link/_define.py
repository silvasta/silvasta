"""
Define the Shape and Behaviour for the Implementations

- Protocols: PortLinker, Emitter, Reflector
- Doc: snapshot of __doc__ from attribute of source
- Side: Port[Protocol] and Plug[Implementation]

- PortLinkData: Combined Docs of one Attr or Cls
- PortLinkRegistry: Track full PortLink Execution

                               DependencyLevel.sstcore.port.link[0]
"""

__all__: list[str] = [
    "PortLinker",
    # render
    "PortEmit",
    "PortPrinter",
    # operate
    "Reflecting",
    "Detecting",
    "Collecting",
    "Projecting",
    "Redacting",
    "DocMerging",
    # storage
    "DunderStore",
    "DunderSet",
    "Channels",
    "Doc",
    "PortDoc",
    "PlugDoc",
    "SidePolicy",
    # types
    "Docs",
    "DocMap",
    "PortDocs",
    "PlugDocs",
    "DocKey",
    "WeakKeyDictionary",
    # data
    "PortLinkData",
    "PortLinkStore",
    "PortLinkCollect",
    "LinkRegistry",
]

import os
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial
from types import MappingProxyType as _FixMap
from typing import Any, NamedTuple, Protocol, TypedDict
from weakref import WeakKeyDictionary, WeakSet

from .._raise import PortLinkError  # TODO: use Raiser?
from .._types import _Stringable


class PortLinker[C, P](Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


#  LINE: -- Reflecting Pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Reflecting(Protocol):  # NEXT: this is now bigger?
    def __call__(self, target: Any, attr: str, /) -> Any:
        """Extract the attribute value from the target"""


class Detecting(Protocol):
    def __call__(self, target: Any, attr: str, /) -> Any:
        """Extract the attribute value from the target"""


class Projecting(Protocol):
    def __call__(self, target: Any, value: Any, /, attr: str) -> str:
        """Attach the new attribute value into the target"""


class Collecting(Protocol):
    def __call__(self, port: type, plug: type, attr: str, /) -> PortLinkCollect:
        """Harvest data in both sides MRO pipeline"""


class Redacting(Protocol):
    def __call__(self, docs: Docs, /) -> str:
        """Format and Render Protocol and Implementation docstrings"""


class DocMerging(Protocol):
    """Callable policy that formats validated Port and Plug doc sequences into a docstring."""

    def __call__(
        self, port: Sequence[PortDoc], plug: Sequence[PlugDoc]
    ) -> list[str]: ...


#  LINE: -- Config -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LinkConfig(Protocol):
    """The Parts needed for operators"""

    @property
    def emit(self) -> PortEmit: ...
    @property
    def printer(self) -> PortPrinter: ...
    def ignores(self, base: type) -> bool: ...
    def show_result(self, docs: SortedDocs, /): ...

    dunders: frozenset[str]


class RenderTheme(TypedDict, total=False):
    """Sub-config for Redactor/Printer panel colors."""

    stat: str
    fail: str
    port: str
    plug: str


@dataclass
class DefaultTheme:
    stat: str = "cyan"
    fail: str = "orange_red1"
    port: str = "purple"
    plug: str = "green"


class LinkInput(TypedDict, total=False):
    env_var: str
    toggle: Iterable[str]
    trace_init: bool | None
    use_loguru: bool | None
    report: int
    theme: RenderTheme
    merge: DocMerging
    skip: frozenset[type]
    dunders: frozenset[str]


#  LINE: -- Emitting Pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PortEmit[**P](Protocol):
    def __call__(self, *args, sender: Any = None, **kwargs) -> None:
        """Define the message structure of port internal events"""


class PortPrinter(Protocol):
    def __call__(self, *args, **kwargs): ...
    def line(self, *targets, color): ...
    def panel(self, content, /, title=None, color="cyan"): ...
    def table(
        self,
        target: dict,
        show_key_type: bool = False,
        show_value_type: bool = True,
        /,
        color: str = "green",
    ) -> None: ...
    def show_sort_result(self, docs: SortedDocs, level=2): ...
    def overview(self, portlink: Any, registry: LinkRegistry, /): ...


#  LINE: -- Dunders (PortOperator.__getattr__) -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class DunderStore(Protocol):  # MOVE: _define
    def __init__(self, dunders: Iterable[str] = ()): ...
    def get(self, name: str, *args, **kwargs) -> str | None: ...


class DunderSet(frozenset):
    @staticmethod
    def format(item: _Stringable, /) -> str:
        return f"__{DunderSet.extract(item)}__"

    @staticmethod
    def extract(item: _Stringable, /) -> str:
        return str(item).strip("_")

    def __new__(cls, items: Iterable[str] = (), /):
        return super().__new__(cls, (cls.format(item) for item in items))

    def __contains__(self, target: Any) -> bool:
        return super().__contains__(self.format(target))

    def get(self, item: str, default=None) -> str | None:
        # TODO: check __getitem__ and directly bind invoke?
        return dunder if (dunder := self.format(item)) in self else default


#  LINE: -- Debug Channels by EnvVar (Tap) -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Channels(frozenset):
    """Guard the active Channels and Rules for Matching"""

    def __new__(cls, env_var="SST_DEBUG", default=()):
        env: tuple[str, ...] = (*os.getenv(env_var, "").split(","), *default)
        return super().__new__(cls, (c for e in env if (c := cls.format(e))))

    def __contains__(self, target: Any) -> bool:
        """Check if the target matches an active channel"""
        if not self or target is None:
            return False
        target: str = (
            target.lower() if isinstance(target, str) else self.key(target)
        )
        if "port.link" in target and not self.has("link"):
            return False
        if self.has("*"):
            return True
        return any(scope in target for scope in super().__iter__())

    def has(self, flag: str, /) -> bool:
        """Check formatted flag directly (bypass wildcard/substring match)"""
        return super().__contains__(self.format(flag))

    @classmethod
    def format(cls, target: str, /) -> str:
        return target.strip().lower()

    @classmethod
    def key(cls, target: Any, /) -> str:
        """The identifier for Member matching"""
        module: str = getattr(target, "__module__", "")
        qualname: str = getattr(target, "__qualname__", "")
        qualname: str = qualname or getattr(type(target), "__qualname__", "")
        return f"{module}.{qualname}"


#  LINE: -- __doc__ Snapshot  -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Doc(NamedTuple):
    """Store atomic __doc__ text from attributes mounted to source (owner)"""

    text: str
    attr: str
    source: type

    @property
    def key(self) -> DocKey:
        return (self.attr, self.source)


class PortDoc(Doc):
    """Keep the Data for Protocols from the Port"""


class PlugDoc(Doc):
    """Keep the Data for Implementations outside Port"""


#  LINE: -- TypeAlias -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type Docs = Sequence[Doc]
type DocMap = Mapping[DocKey, Doc]

type PortDocs = Sequence[PortDoc]
type PlugDocs = Sequence[PlugDoc]

type DocKey = tuple[str, type]

type WeakTypeDict = WeakKeyDictionary[type, WeakSet[type]]


#  LINE: -- Side: Port-Plug -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SidePolicy(StrEnum):
    """Define Rules for the PortDoc and PlugDoc DTO and provide Access"""

    PORT = auto()
    PLUG = auto()

    @classmethod
    def assess(cls, data: Doc, /) -> SidePolicy:
        """Get the corresponding Policy type"""
        match data:
            case PortDoc():
                return cls.PORT
            case PlugDoc():
                return cls.PLUG
        raise ValueError(f"{cls} got invalid side: {data}")

    @property
    def ctor(self) -> type[PortDoc | PlugDoc]:
        """Get the corresponding Doc class"""
        match self:
            case self.PORT:
                return PortDoc
            case self.PLUG:
                return PlugDoc

    def validate(self, data: Doc, /) -> bool:
        """Check if Doc is valid for selected Policy"""
        match self:
            case self.PORT:
                if not isinstance(data, PortDoc):
                    return False
                return issubclass(data.source, Protocol)
            case self.PLUG:
                if not isinstance(data, PlugDoc):
                    return False
                return not issubclass(data.source, Protocol)

    @classmethod  # NOTE: partition fails for str.partition overwrite...
    def sort(cls, docs: Docs, /) -> SortedDocs:
        port: PortDocs = []
        plug: PlugDocs = []
        fail: Docs = []
        for doc in docs:
            match doc:
                case PortDoc():
                    port.append(doc)
                case PlugDoc():
                    plug.append(doc)
                case _:
                    fail.append(doc)
        return SortedDocs(port, plug, fail)


class SortedDocs(NamedTuple):
    port: PortDocs
    plug: PlugDocs
    fail: Docs

    def port_and_plug(self) -> tuple[list[PortDoc], list[PlugDoc]]:
        return list(self.port), list(self.plug)

    def __str__(self):
        return type(self).__name__

    def __bool__(self) -> bool:
        return len(self.port) != 0 or len(self.plug) != 0 or len(self.fail) != 0

    def __repr__(self):
        port: int = len(self.port)
        plug: int = len(self.plug)
        fail: int = len(self.fail)
        total: int = port + plug + fail
        return f"{self}[{port=}, {plug=}, {fail=}, {total=}]"


#  LINE: -- Link Data -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PortLinkData:
    """Store portlink docs, keep insertion order, unique by (attr, source)"""

    __slots__ = ("data",)

    data: Mapping[DocKey, Doc]

    def __iter__(self) -> Iterator[Doc]:
        return iter(self.data.values())

    def __len__(self) -> int:
        return len(self.data)

    def __contains__(self, item: object) -> bool:
        match item:
            case Doc() as doc:
                return doc.key in self.data
            case (str() as attr, type() as source):
                return (attr, source) in self.data
            case type() as source:
                return any(doc.source is source for doc in self)
            case str() as attr:
                return any(doc.attr == attr for doc in self)
            case _:
                return False

    def __getitem__(self, access: str | type | DocKey) -> list[Doc]:
        """Centralized and Error free access to key columns"""
        match access:
            case str() as attr:
                return [doc for doc in self if doc.attr == attr]
            case type() as source:
                return [doc for doc in self if doc.source is source]
            case (str() as attr, type() as source):
                return [doc] if (doc := self.data.get((attr, source))) else []
            case _:
                return []

    def __str__(self) -> str:
        return f"{type(self).__name__}[{len(self)}]"

    def __repr__(self) -> str:
        return f"{self}[{self.attrs}][{self.sources}]({self.data})"

    @property
    def attrs(self) -> frozenset[str]:
        """Get a unique set of all tracked attributes"""
        return frozenset(doc.attr for doc in self)

    @property
    def sources(self) -> frozenset[type]:
        """Get a unique set of all tracked attributes"""
        return frozenset(doc.source for doc in self)


class PortLinkStore(PortLinkData):
    """Unmutable Link Mapping for Storing the Docs"""

    __slots__ = ()

    def __init__(self, data: Docs | DocMap = ()):
        match data:
            case Mapping() as mapping:
                self.data: _FixMap[DocKey, Doc] = _FixMap(mapping)  # ty:ignore
            case Sequence() as sequence:
                self.data: _FixMap[DocKey, Doc] = _FixMap(
                    mapping={doc.key: doc for doc in sequence}
                )

    def edit(self) -> PortLinkCollect:
        """Spawn mutable BaseLinks pre-filled with this data"""
        return PortLinkCollect(self.data)


class PortLinkCollect(PortLinkData):
    """Mutable Link Mapping for Collecting the Docs"""

    __slots__ = ()

    def __init__(self, data: Docs | DocMap = ()):
        self.data: dict[DocKey, Doc] = {}  # ty:ignore
        self.fill(data)

    def absorb(self, data: PortLinkData, /):
        for doc in data:
            self.fill(doc)

    def fill(self, data: Doc | Docs | DocMap, /):
        """Add new Doc Mapping entries if they are not already covered"""
        # IDEA: return True, or 1/count for added? where to measure?
        # - raise in __setitem__?? len(before)+len(data)==len(after)??
        match data:
            case Doc() as doc:
                self[doc.key] = doc
            case Mapping():
                for key, value in data.items():
                    self[key] = value
            case Sequence():
                for doc in data:
                    self[doc.key] = doc

    def __setitem__(self, access: DocKey, value: Doc):
        """Simple Error free write access"""
        if not value.text:  # TODO: special error to easily filter at catch
            raise PortLinkError(f"Reject Empty Doc! {access=}, {value=}")
        if access not in self.data:
            self.data[access] = value

    def save(self) -> PortLinkStore:
        """Freeze the current state and return the read-only BaseLinkDocs"""
        return PortLinkStore(self.data)


#  LINE: -- Global Type Tracking -- -- - -- -- - -- -- - -- -- - -- -- - -- --

_weak_dict_field = partial(
    field, default_factory=WeakKeyDictionary, init=False, repr=False
)


@dataclass(slots=True)  # WARN: what about that??
class LinkRegistry:
    """
    Weak M:N topological index of (Protocol <-> Implementation) links

    - _by_port: Map Protocol -> WeakSet of Implementation
    - _by_plug: Map Implementation -> WeakSet of Protocol

    - ports/plugs: return tuple to avoid GC removes provided types

    """

    _by_port: WeakTypeDict = _weak_dict_field()
    _by_plug: WeakTypeDict = _weak_dict_field()

    def register(self, port: type, plug: type) -> None:
        """Record a direct @portlink(port) application on plug"""
        if port not in self._by_port:
            self._by_port[port] = WeakSet()
        self._by_port[port].add(plug)

        if plug not in self._by_plug:
            self._by_plug[plug] = WeakSet()
        self._by_plug[plug].add(port)

    def ports(self) -> tuple[type, ...]:
        """All currently alive Protocols that have at least one implementation"""
        return tuple(p for p, plugs in self._by_port.items() if len(plugs) > 0)

    def plugs(self) -> tuple[type, ...]:
        """All currently alive decorated Implementation classes"""
        return tuple(c for c, ports in self._by_plug.items() if len(ports) > 0)

    def links(self) -> Iterator[tuple[type, type]]:
        """Yield all active (port, plug) pairs"""
        for port, plugs in list(self._by_port.items()):
            for plug in tuple(plugs):
                yield (port, plug)

    def implementations_of(self, port: type) -> tuple[type, ...]:
        """Return all Implementations linked to specific Protocol"""
        plugs: WeakSet[type] | None = self._by_port.get(port)
        return tuple(plugs) if plugs is not None else ()

    # IDEA: just __getitem__ ? caller knows if port/plug, this could be shorter?

    def protocols_of(self, plug: type) -> tuple[type, ...]:
        """Return all Protocols linked to specific Implementation"""
        ports: WeakSet[type] | None = self._by_plug.get(plug)
        return tuple(ports) if ports is not None else ()

    def __str__(self):
        return f"{type(self).__name__}[{self.stats()}]"

    def stats(self) -> dict[str, int]:
        return {
            "ports": len(self.ports()),
            "plugs": len(self.plugs()),
            "links": sum(len(plugs) for plugs in self._by_port.values()),
        }
