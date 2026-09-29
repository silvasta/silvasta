"""
Data

- temporary module
"""

import enum as _e
import typing as _t
from collections.abc import Mapping as _Mapping
from collections.abc import Sequence as _Sequence
from dataclasses import dataclass as _dataclass
from dataclasses import replace as _replace
from types import MappingProxyType as _FixMap

from ..govern import EnumMachine
from ._printer import printer

type Docs = _Sequence[Doc]
type DocMap = _Mapping[DocKey, Doc]

type PortDocs = _Sequence[PortDoc]
type PlugDocs = _Sequence[PlugDoc]


type DocKey = tuple[str, type]


class PortEmit[**P](_t.Protocol):
    def __call__(self, *arg: P.args, **kwarg: P.kwargs) -> None: ...


class PortLinker[C, P](_t.Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


class DocMerger(_t.Protocol):  # IDEA: Merging? only if as well operator
    def __call__(self, docs: Docs) -> str:
        """Format and Render Protocol and Implementation docstrings"""


class Reflecting(_t.Protocol):
    def __call__(self, target: _t.Any, attr: str, /) -> _t.Any:
        """Extract the attribute value from the target"""


class Injecting(_t.Protocol):
    def __call__(self, target: _t.Any, value: _t.Any, /, attr: str) -> str:
        """Attach the new attribute value into the target"""


class Collecting(_t.Protocol):
    def __call__(self, port: type, plug: type, attr: str, /) -> PortLinks:
        """Harvest data in both sides MRO pipeline"""


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


def _merger(docs) -> str:
    raise NotImplementedError("Override in PortLink.core")


@_dataclass(frozen=True, slots=True)
class LinkSpec:
    skip: frozenset[type] = frozenset({object, _t.Protocol, _t.Generic})
    on_exit_with_error: bool = True  # TODO:
    merge: DocMerger = _merger
    emit: PortEmit | None = None

    def ignores(self, base: type) -> bool:
        return base in self.skip

    def note(self, event: _t.Any) -> None:
        if self.emit is not None:
            self.emit(event)

    def derive(self, **kwargs) -> _t.Self:
        return _replace(self, **kwargs)

    def surface(self, protocol: type) -> list[str]:
        cls_as_attribute: list[str] = [""]
        return cls_as_attribute + list(_t.get_protocol_members(protocol))


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


class MergeMachine(EnumMachine):
    Schema1 = _e.auto()

    def __call__(self, docs: Docs, spec: LinkSpec | None = None) -> str:
        _spec_to_emit_and_format: LinkSpec = spec or LinkSpec()
        port: list[Doc] = []
        plug: list[Doc] = []
        fail: list[Doc] = []
        for doc in docs:
            printer.line(color="cyan")
            match doc:
                case PortDoc():
                    self.sort_for_port(doc, port, fail)
                case PlugDoc():
                    self.sort_for_plug(doc, plug, fail)
        self.handle_sort(port, plug, fail)
        match self:
            case self.Schema1:
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
        printer.panel(f"Statsistic: Total (multi) lines: {len(lines)}")
        return lines

    def format_port_header(self, first: Doc, lines: list[str]):
        lines.append(first.text.strip("\n"))
        printer(f"Attached Port header: {first.key}")

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
        printer.panel(
            f"Stats: port: {len(port)}, plug: {len(plug)}, fail: {len(fail)} "
        )
        if not plug:
            printer.panel("Implementation", frame="yellow", title="Missing")
        if not port:
            printer.panel("Definitions", frame="orange", title="Missing")
        if fail:
            printer.panel(*fail, frame="red", title="Failed")

    def sort_for_port(self, doc: Doc, port: list, fail: list) -> None:
        if SidePolicy.PORT.validate(doc):
            port.append(doc)
            printer(f"Accepted: {doc.key}")
        else:
            fail.append(doc)
            printer(f"Rejected: {doc.key}")

    def sort_for_plug(self, doc: Doc, plug: list, fail: list) -> None:
        if SidePolicy.PLUG.validate(doc):
            plug.append(doc)
            printer(f"Accepted: {doc.key}")
        else:
            fail.append(doc)
            printer(f"Rejected: {doc.key}")
