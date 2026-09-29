"""
The Model and Data Definition

- Designed to test the limits while still producing results

"""

__all__: list[str] = [
    "PortLinkDocs",
    "PortLinks",
    "PortLinkData",
    "SidePolicy",
    # dto
    "Doc",
    "PortDoc",
    "PlugDoc",
    # types
    "Docs",
    "DocMap",
    "PortDocs",
    "PlugDocs",
    "DocKey",
]


import enum as _e
import typing as _t
from collections.abc import Mapping as _Mapping
from collections.abc import Sequence as _Sequence
from types import MappingProxyType as _FixMap

type Docs = _Sequence[Doc]
type DocMap = _Mapping[DocKey, Doc]

type PortDocs = _Sequence[PortDoc]
type PlugDocs = _Sequence[PlugDoc]


type DocKey = tuple[str, type]


class Doc(_t.NamedTuple):
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


class PortLinkData:
    """Store portlink docs, keep insertion order, unique by (attr, source)"""

    __slots__ = ("data",)

    data: _Mapping[DocKey, Doc]

    def __iter__(self) -> _t.Iterator[Doc]:
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
        """Centralized and Error free access to key collumns"""
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


class PortLinkDocs(PortLinkData):
    __slots__ = ()

    def __init__(self, data: Docs | DocMap = ()):
        match data:
            case _Mapping() as mapping:
                self.data: _FixMap[DocKey, Doc] = _FixMap(mapping)
            case _Sequence() as sequence:
                self.data: _FixMap[DocKey, Doc] = _FixMap(
                    mapping={doc.key: doc for doc in sequence}
                )

    def edit(self) -> PortLinks:
        """Spawn mutable BaseLinks pre-filled with this data"""
        return PortLinks(self.data)


class PortLinks(PortLinkData):
    __slots__ = ()

    def __init__(self, data: Docs | DocMap = ()):
        self.data: dict[DocKey, Doc] = {}
        self.fill(data)

    def absorb(self, data: PortLinkData, /):
        for doc in data:
            self.fill(doc)

    def fill(self, data: Doc | Docs | DocMap, /):
        """Add new Doc Mapping entires if they are not already covered"""
        # IDEA: return True, or 1 for addad
        match data:
            case Doc() as doc:
                self[doc.key] = doc
            case _Mapping():
                for key, value in data.items():
                    self[key] = value
            case _Sequence():
                for doc in data:
                    self[doc.key] = doc

    def __setitem__(self, access: DocKey, value: Doc):
        # IDEA: return True, or 1 for addad
        """Simple Error free write access"""
        if not value.text:
            print("EMpty")
        if access not in self.data:
            self.data[access] = value

    def save(self) -> PortLinkDocs:
        """Freeze the current state and return the read-only BaseLinkDocs"""
        return PortLinkDocs(self.data)


class SidePolicy(_e.StrEnum):
    """Define Rules for the PortDoc and PlugDoc DTO and provide Access"""

    PORT = _e.auto()
    PLUG = _e.auto()

    @classmethod
    def assess(cls, data: Doc, /) -> SidePolicy:
        """Get the corresponding Policy type"""
        match data:
            case PortDoc():
                return cls.PORT
            case PlugDoc():
                return cls.PLUG
        raise ValueError(f"{cls} got invalid side: {data}")

    def validate(self, data: Doc, /) -> bool:
        """Check if Doc is valid for selected Policy"""
        match self:
            case self.PORT:
                if not isinstance(data, PortDoc):
                    return False
                return issubclass(data.source, _t.Protocol)
            case self.PLUG:
                if not isinstance(data, PlugDoc):
                    return False
                return not issubclass(data.source, _t.Protocol)

    @property
    def retrieve(self) -> type[PortDoc | PlugDoc]:
        """Get the corresponding Doc type"""
        match self:
            case self.PORT:
                return PortDoc
            case self.PLUG:
                return PlugDoc
