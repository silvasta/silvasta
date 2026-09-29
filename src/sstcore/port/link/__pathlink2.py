"""
Reference the Implementations back to their Definitions in the port

- Link and Sync docstrings at import time
  - Use docstring from sstcore.port as Single-Source-of-Truth (SSoT)
  - Append optional local docstring with implementation details

- Provide simple IDE navigation hook like in nvim: 'gd'

- Trigger static type checker warning on implementation mismatch

"""

__all__: list[str] = [
    "portlink",
    "PortLink",
    "PortLinker",
    "DocMerger",
]

import typing as _t
from dataclasses import dataclass as _dataclass
from dataclasses import replace as _replace
from functools import cached_property as _cached_property
from inspect import cleandoc as _cleandoc
from inspect import getattr_static as _getattr_static


class PortLinker[C, P](_t.Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


class DocMerger(_t.Protocol):
    def __call__(self, source: str, target: str, /, joint: str = "") -> str:
        """Concatenate Protocol and Implementation docstring"""


def default_merge(source: str, target: str, /, joint: str = "") -> str:
    return f"""{source}{joint}{target}"""


@_dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    joint: str = "\n\n[Implementation Notes]\n"
    _merge: DocMerger = default_merge

    def merge(self, source: str, target: str, /) -> str:
        return self._merge(source, target, joint=self.joint)

    def create(
        self, *, merge: DocMerger | None = None, joint: str | None = None
    ) -> _t.Self:
        return _replace(
            self,
            joint=self.joint if joint is None else joint,
            _merge=self._merge if merge is None else merge,
        )

    def __call__[C, P](self, protocol: type[P], /) -> PortLinker[C, P]:
        """Merge docstrings and enforce static type check"""

        def portlinker(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)

            if proto_doc := _detect(protocol):
                top_level_doc: str = (
                    proto_doc
                    if not (cls_doc := _detect(cls))
                    else self.merge(proto_doc, cls_doc)
                )
                _inject(cls, top_level_doc)

            for attr_name in _t.get_protocol_members(protocol):
                if (
                    (proto_attr := _reflect(protocol, attr_name))
                    and (proto_doc := _detect(proto_attr))
                    and (target_attr := _reflect(cls, attr_name))
                ):
                    resulting_doc: str = (
                        proto_doc
                        if not (target_doc := _detect(target_attr))
                        else self.merge(proto_doc, target_doc)
                    )
                    _inject(target_attr, resulting_doc)

            return cls

        return portlinker


portlink = PortLink()  # TARGET: the main object


#  LINE: -- Internal Logic -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _extract(cls: type, name: str) -> _t.Any | None:
    """Safely extract attribute without invoking __get__"""
    try:
        return _getattr_static(cls, name)
    except AttributeError:
        return None


def _reflect(cls: type, name: str, /) -> _t.Any | None:
    """Extract attribute and manage special forms"""
    attr: _t.Any | None = _extract(cls, name)
    if isinstance(attr, (classmethod, staticmethod)):
        return attr.__func__
    if callable(attr) or isinstance(attr, (property, _cached_property)):
        return attr
    return None


def _detect(target: _t.Any, /) -> str:  #
    doc: str | None = getattr(target, "__doc__", None)
    return _cleandoc(doc) if doc else ""


def _inject(target: _t.Any, doc: str, /) -> None:
    """Safely attach the doc to the target attr or cls"""
    try:
        target.__doc__ = doc
    except AttributeError, TypeError:
        return


#  LINE: -- Possible Improvements -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _find_defining_class(cls: type, name: str) -> type | None:
    for base in cls.__mro__:
        if name in base.__dict__:
            return base
    return None


# AI:: this and PortLink.merge accepting a list -> manage order
def _harvest_docs(cls: type, attr_name: str) -> _t.Iterator[_DocContext]:
    """Yield docstrings for an attribute from the MRO hierarchy."""
    for base in cls.__mro__:
        if attr_name in base.__dict__:
            attr = base.__dict__[attr_name]
            if doc := getattr(attr, "__doc__", None):
                yield _DocContext(defining_class=base, docstring=doc.strip())


def _collect_fragments(
    protocol: type, impl: type, attr_name: str
) -> list[_DocFragment]:
    """Walk both MROs and collect docstrings for this attribute."""
    fragments: list[_DocFragment] = []

    # Protocol side (source of truth)
    for base in protocol.__mro__:
        if attr := _reflect(base, attr_name):
            if doc := _detect(attr):
                fragments.append(
                    _DocFragment(base, attr_name, doc, "protocol")
                )

    # Implementation side
    for base in impl.__mro__:
        if attr := _reflect(base, attr_name):
            # Only record if defined directly on this base (avoid duplicates)
            if attr_name in base.__dict__ and (doc := _detect(attr)):
                fragments.append(
                    _DocFragment(base, attr_name, doc, "implementation")
                )

    return fragments
