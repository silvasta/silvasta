"""
collect

.
"""

import typing as _t
from inspect import cleandoc as _cleandoc

from .data import Doc, PlugDoc, PortDoc, Side, spec

# NEXT:
# NEXT:
# NEXT:
# NEXT:


def _harvest(protocol: type, cls: type, attr_name: str) -> list[Doc]:
    """Collect deduplicated Doc from Protocol and Implementation MROs."""
    parts: list[Doc] = []
    seen_texts: set[str] = set()

    for side, root in [("proto", protocol), ("impl", cls)]:
        for origin in _extract_origins(root, attr_name, side):  # type: ignore
            if origin.text not in seen_texts:
                seen_texts.add(origin.text)
                parts.append(origin)

    return parts


def _detect(
    cls: type,
    name: str = "",
    /,
    *,
    side: Side,
    reverse: bool,
) -> list[Doc]:
    """Collect original Doc along one MRO. ``reverse=True`` → earliest first."""
    bases: list[type] = [
        base for base in cls.__mro__ if not spec.ignores(base)
    ]
    if reverse:
        bases.reverse()

    out: list[Doc] = []
    for base in bases:
        payload: object | None = _payload(base, name)
        if payload is None:
            continue
        text: str = _own_text(base, name, side, payload)
        if not text:
            continue
        out.append(Doc(side, base, text, name))
    return out


def _get_raw_doc(target: _t.Any) -> str:
    """Retrieve pristine docstring without triggering descriptor execution."""
    if isinstance(target, type):
        if "__portlink_raw_doc__" in target.__dict__:
            return target.__dict__["__portlink_raw_doc__"]
        doc = target.__dict__.get("__doc__")
        return _cleandoc(doc) if isinstance(doc, str) else ""

    if hasattr(target, "__portlink_raw_doc__"):
        return target.__portlink_raw_doc__

    doc = getattr(target, "__doc__", None)
    return _cleandoc(doc) if isinstance(doc, str) else ""


def _stash_raw_doc(target: _t.Any) -> None:
    # NEXT: Reflect and Inject
    """Capture author's pristine docstring before mutation occurs."""
    if isinstance(target, type):
        if "__portlink_raw_doc__" not in target.__dict__:
            doc = target.__dict__.get("__doc__")
            cleaned = _cleandoc(doc) if isinstance(doc, str) else ""
            try:
                target.__portlink_raw_doc__ = cleaned
            except AttributeError, TypeError:
                pass
        return

    if not hasattr(target, "__portlink_raw_doc__"):
        doc = getattr(target, "__doc__", None)
        cleaned = _cleandoc(doc) if isinstance(doc, str) else ""
        try:
            target.__portlink_raw_doc__ = cleaned
        except AttributeError, TypeError:
            pass


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#
def _collect_class_docs(
    protocol: type, impl: type
) -> tuple[list[Doc], list[Doc]]:
    """Collect class docstrings: Latest -> Earliest (Forward MRO order)."""
    protos: list[Doc] = []
    impls: list[Doc] = []
    seen: set[type] = set()

    for base in protocol.__mro__:
        if spec.ignores(base):
            continue
        text = _get_raw_doc(base)
        if text and base not in seen:
            seen.add(base)
            protos.append(Doc(side="proto", owner=base, text=text))

    for base in impl.__mro__:
        if spec.ignores(base):
            continue
        text = _get_raw_doc(base)
        if text and base not in seen:
            seen.add(base)
            impls.append(Doc(side="impl", owner=base, text=text))

    return protos, impls


def _collect_attr_docs(
    protocol: type, impl: type, attr_name: str
) -> tuple[list[Doc], list[Doc]]:
    protos: list[Doc] = []
    impls: list[Doc] = []
    seen: set[type] = set()

    # Protocol side: Earliest (Root) -> Latest (Leaf)
    for base in reversed(protocol.__mro__):
        if spec.ignores(base):
            continue
        if attr_name in base.__dict__:
            raw = _reflect(base, attr_name)
            _stash_raw_doc(raw)
            text = _get_raw_doc(raw)
            if text and base not in seen:
                seen.add(base)
                protos.append(Doc(side="proto", owner=base, text=text))

    # Implementation side: Earliest (Root) -> Latest (Leaf)
    for base in reversed(impl.__mro__):
        if spec.ignores(base):
            continue
        if attr_name in base.__dict__:
            raw = _reflect(base, attr_name)
            _stash_raw_doc(raw)
            text = _get_raw_doc(raw)
            if text and base not in seen:
                seen.add(base)
                impls.append(Doc(side="impl", owner=base, text=text))

    return protos, impls


def _collect_class_docs(protocol: type, impl: type) -> list[Doc]:
    docs: list[Doc] = []
    seen: set[tuple] = set()

    # Protocols first (latest protocol doc first, as requested)
    for base in protocol.__mro__:
        if base in (object, _t.Protocol, _t.Generic):
            continue
        text = _detect(base)  # class doc
        if text:
            dd = ___Doc("proto", base, "", text)
            # EXTRACT:
            if dd.key() not in seen:
                seen.add(dd.key())
                docs.append(dd)

    # Implementations
    for base in impl.__mro__:
        if base in (object, _t.Protocol, _t.Generic):
            continue
        # Only consider classes that actually define a docstring
        if "__doc__" in base.__dict__ or base is impl:
            text = _detect(base)
            if text:
                dd = Doc("impl", base, "", text)
                if dd.key() not in seen:
                    seen.add(dd.key())
                    docs.append(dd)

    return docs


def _collect_attr_docs(protocol: type, impl: type, attr: str) -> list[Doc]:
    # EXTRACT:
    docs: list[Doc] = []
    seen: set[tuple] = set()

    # Protocol side (earliest protocol first for attributes)
    for base in reversed(protocol.__mro__):  # reversed = earliest first
        if base in (object, _t.Protocol, _t.Generic):
            continue
        if _attr := _reflect(base, attr):
            if text := _detect(_attr):
                dd = PortDoc(text, attr, base)
                if dd.key() not in seen:
                    seen.add(dd.key())
                    docs.append(dd)

    # Implementation side (definition order in MRO)
    for base in impl.__mro__:
        if base in (object, _t.Protocol, _t.Generic):
            continue
        if _attr := _reflect(base, attr):
            if text := _detect(_attr):
                dd = PlugDoc(text, attr, base)
                if dd.key() not in seen:
                    seen.add(dd.key())
                    docs.append(dd)

    return docs


def _collect_fragments(
    protocol: type, impl: type, attr_name: str | None = None
) -> list[Doc]:
    """Walk both MROs following the exact ordering rules you specified."""
    fragments: list[Doc] = []
    seen: set[tuple[type, str]] = set()

    # Protocol side
    proto_mro = [b for b in protocol.__mro__ if spec.ignores(b)]
    if attr_name is None:  # class doc: latest protocol first
        proto_mro = list(reversed(proto_mro))

    for base in proto_mro:
        if attr_name is None:
            text = _extract_clean_doc(base)
            _target = base
        else:
            member = _reflect(base, attr_name)
            text = _extract_clean_doc(member) if member is not None else ""
            _target = member or base

        if text and (base, text) not in seen:
            seen.add((base, text))
            fragments.append(Doc(base, attr_name, text, True))

    # Implementation side (always most-derived first)
    for base in impl.__mro__:
        if not spec.ignores(base):
            continue
        if attr_name is None:
            text = _extract_clean_doc(base)
        else:
            member = base.__dict__.get(attr_name)
            text = _extract_clean_doc(member) if member is not None else ""
        if text and (base, text) not in seen:
            seen.add((base, text))
            fragments.append(Doc(base, attr_name, text, False))

    return fragments
