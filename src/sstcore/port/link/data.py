"""
Data

- temporary module
"""

import typing as _t

from .._field import FixTypeField

type Docs = _t.Sequence[Doc]
type PortDocs = _t.Sequence[PortDoc]
type PlugDocs = _t.Sequence[PortDoc]


type Side = _t.Literal["port", "plug"]
type DocKey = tuple[str, type]


class Doc(_t.NamedTuple):
    # CHECK: relative MRO level?
    """Store atomic __doc__ text from attr mounted to source cls (owner)"""

    text: str
    attr: str
    source: type

    @property
    def key(self) -> tuple:
        return (self.attr, self.source)

    @property
    def side(self) -> Side:
        raise NotImplementedError

    def valid(self, source: type) -> bool:  # REMOVE: when never needed...
        return self.side == "port" and isinstance(source, _t.Protocol)


class PortDoc(Doc):
    @property
    def side(self) -> Side:
        return "port"


class PlugDoc(Doc):
    @property
    def side(self) -> Side:
        return "plug"


class PortLinkDocs:
    """Store portlink docs, keep insertion order, unique by (attr, source)"""

    __slots__ = ("_docs", "_keys")

    def __init__(self, docs: _t.Iterable[Doc] = (), /):
        seen: dict[DocKey, Doc] = {}
        for doc in docs:  # first text wins
            seen.setdefault(doc.key, doc)
        self._docs: tuple[Doc, ...] = tuple(seen.values())
        self._keys: frozenset[DocKey] = frozenset(seen)

    def __contains__(self, item: Doc | DocKey | type) -> bool:
        if isinstance(item, Doc):
            item: DocKey = item.key
        elif isinstance(item, type):
            item: DocKey = ("", item)  # class-level visit, not "any attr"
        return item in self._keys

    def __iter__(self) -> _t.Iterator[Doc]:
        # IDEA: create other iterator that yields first over attr, then over sources
        # - ok maybe first iterator is just over self._keys to get attr
        #   - then enter attr to iterate over all sources, or just get list is fine as well
        return iter(self._docs)

    def __len__(self) -> int:  # CHECK: needed?
        return len(self._docs)

    def __getitem__(self, index: int) -> Doc:  # CHECK: absorb Links.get?
        # NEXT: needed, all docs from 1 attr, plus first occurance
        # - take first from self._docs, others from _keys, order still matters..!!
        # - the relative mro-level on Doc still looks best
        return self._docs[index]

    def get(self, attr: str, source: type) -> Doc | None:
        # CHECK: combine with __getitem__??
        if (key := (attr, source)) not in self._keys:
            return None
        return next(doc for doc in self._docs if doc.key == key)

    @property
    def as_list(self) -> list[Doc]:
        """Provide high class readable name (in combination)"""
        return [*self._docs]


#  LINE: -- Config -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LinkSpec:  # LATER: make it separable, formatter, portlink-app, ...
    name = FixTypeField[str](types=str)
    skip = FixTypeField[frozenset[type]](types=frozenset)
    on_exit_with_error: bool = True

    def __init__(self, *, skip: frozenset[type]) -> None:
        self.skip: frozenset[type] = skip

    def ignores(self, base: type) -> bool:
        return base in self.skip


_SKIP: frozenset[type] = frozenset({object, _t.Protocol, _t.Generic})

spec = LinkSpec(skip=_SKIP)


def _test1(args: Doc):
    x = args[0]
    y = args[1]
    z = args[2]
    a, b, c = args
    print(a, b, c, x, y, z)  # mute ruff


if __name__ == "__main__":
    port = PortDoc("proto doc", attr="", source=LinkSpec)
    plug = PlugDoc("impls doc", attr="", source=LinkSpec)

    _test1(Doc("test", "attr", LinkSpec))
