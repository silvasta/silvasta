"""
data

.
"""

import typing as _t

from .._field import FixTypeField

type _Docs = _t.Sequence[Doc]
type _DocSet = frozenset[Doc]
type _DocList = list[Doc]


type _Side = _t.Literal["port", "plug"]


class PortLinker[C, P](_t.Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


class DocMerger(_t.Protocol):
    def __call__(
        self, ports: _Docs, plugs: _Docs, /, *, spec: LinkSpec | None = None
    ) -> str:
        """Concatenate Protocol and Implementation docstrings"""


class Doc(_t.NamedTuple):  # IDEA: mro-index/level,...
    """
    One atomic Docstring Contribution

    __doc__ text from attribute mounted to source cls (owner)
    """

    text: str
    attr: str
    source: type

    @property
    def side(self) -> _Side:
        raise NotImplementedError

    def __hash__(self):
        # return hash((self.text, self.source, self.attr))
        return hash(self)

    def key(self) -> tuple:
        # TODO: text
        """For deduplication by identity of contribution."""
        return (self.attr, self.source)


class PortDoc(Doc):
    @property
    def side(self) -> _Side:
        return "port"


class PlugDoc(Doc):
    @property
    def side(self) -> _Side:
        return "plug"


class LinkSpec:
    name = FixTypeField[str](types=str)
    skip = FixTypeField[frozenset[type]](types=frozenset)
    on_error: bool = True

    def __init__(self, *, skip: frozenset[type]) -> None:
        self.skip: frozenset[type] = skip

    def ignores(self, base: type) -> bool:
        return base in self.skip


_SKIP: frozenset[type] = frozenset({object, _t.Protocol, _t.Generic})

spec = LinkSpec(skip=_SKIP)
