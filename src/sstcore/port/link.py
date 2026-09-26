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

from ._field import FixTypeField


class PortLinker[C, P](_t.Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


class DocMerger(_t.Protocol):
    def __call__(
        self,
        protos: _Docs,
        impls: _Docs,
        /,
        joint: str = "",  # IDEA: spec?
    ) -> str:
        """Concatenate Protocol and Implementation docstrings"""


type _Docs = _t.Sequence[Doc]


class Doc(_t.NamedTuple):
    text: str
    source: type
    attr: str = ""
    # IDEA: index/level,...


type _Side = _t.Literal["port", "plug"]


class ___Doc(_t.NamedTuple):
    """One atomic docstring contribution."""

    side: _t.Literal["port", "plug"]
    owner: type
    attr: str  # "" for class-level doc
    text: str

    def __hash__(self):
        return hash((self.side, self.owner, self.attr, self.text))

    def key(self) -> tuple:
        """For deduplication by identity of contribution."""
        return (self.side, self.owner, self.attr)


class PortDoc(Doc): ...


class PlugDoc(Doc): ...


def concat_merger(protos: list[Doc], impls: list[Doc], is_class: bool) -> str:
    """Naive 'Concat All' approach with visual headers."""
    seen_texts: set[str] = set()
    lines: list[str] = []

    def _add_fragments(fragments: list[Doc], section_title: str):
        section_added = False
        for frag in fragments:
            if frag.text in seen_texts:
                continue

            if not section_added:
                lines.extend(["", f"{{{section_title}}}", ""])
                section_added = True

            lines.extend([f"[{frag.owner.__name__}]", frag.text, ""])  # ty:ignore
            seen_texts.add(frag.text)

    # Sorting logic based on scope
    ordered_protos = protos if is_class else list(reversed(protos))
    ordered_impls = impls if is_class else list(reversed(impls))

    _add_fragments(ordered_protos, "Definitions from the Port")
    _add_fragments(ordered_impls, "Implementations")

    return "\n".join(lines).strip()


def default_merge(
    protos: list[Doc],
    impls: list[Doc],
    /,
    *,
    title: str | None = None,
) -> str:
    sections: list[str] = []
    seen_texts: set[str] = set()

    if title:
        cleaned_title = _cleandoc(title).strip()
        sections.append(cleaned_title)
        seen_texts.add(cleaned_title)

    filtered_protos: list[Doc] = [
        p
        for p in protos
        if p.text not in seen_texts and not seen_texts.add(p.text)
    ]
    if filtered_protos:
        p_lines: list[str] = ["{Definitions from the Port}"]
        for p in filtered_protos:
            p_lines.append(f"[{p.owner.__name__}]\n{p.text}")
        sections.append("\n\n".join(p_lines))

    filtered_impls: list[Doc] = [
        i
        for i in impls
        if i.text not in seen_texts and not seen_texts.add(i.text)
    ]
    if filtered_impls:
        i_lines: list[str] = ["{Implementations}"]
        for i in filtered_impls:
            i_lines.append(f"[{i.owner.__name__}]\n{i.text}")
        sections.append("\n\n".join(i_lines))

    return "\n\n".join(sections).strip()


def _default_merge(fragments: _Docs) -> str:
    """Exactly the temporary debug-friendly format you asked for."""
    if not fragments:
        return ""

    parts: list[str] = ["{Definitions from the Port}"]
    impl_header_shown = False

    for f in fragments:
        if not f.is_protocol and not impl_header_shown:
            parts.append("\n{Implementations}")
            impl_header_shown = True

        title = f"[{f.owner.__name__}]"
        parts.append(f"{title}\n{f.text.strip()}")

    return "\n\n".join(parts)


def __default_merge(protos: _Docs, impls: _Docs, /, joint: str = "") -> str:
    """Naive renderer: Group by side, stamp the owner."""

    seen: set[str] = set()
    chunks: list[str] = []

    def take(parts: _Docs, /, *, titled: bool) -> list[str]:
        out: list[str] = []
        for part in parts:
            if not part.text or part.text in seen:
                continue
            seen.add(part.text)
            out.append(
                f"[{part.owner.__name__}]\n{part.text}"
                if titled
                else part.text
            )
        return out

    _lead_source: _Docs
    rest_proto: _Docs
    rest_impl: _Docs = impls

    if protos:
        _lead_source, rest_proto = protos[:1], protos[1:]
    else:
        _lead_source, rest_proto = impls[:1], ()
        rest_impl = impls[1:]

    titled_proto: list[str] = take(rest_proto, titled=True)
    if titled_proto:
        chunks.append("{Definitions from the Port}")
        chunks.extend(titled_proto)

    titled_impl: list[str] = take(rest_impl, titled=True)
    if titled_impl:
        chunks.append(joint.strip() or "{Implementations}")
        chunks.extend(titled_impl)

    return "\n\n".join(chunks)


@_dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    joint: str = "{Implementations}"  # LATER: specified config!
    _merge: DocMerger = default_merge

    def merge(self, protos: _Docs, impls: _Docs, /) -> str:
        return self._merge(protos, impls)

    def setup(
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

            # CHECK: dispatch by ProtoDoc(Doc)??
            proto_data: list[Doc] = _detect(
                protocol, "", side="proto", reverse=False
            )
            # TODO: return on empty proto?
            impl_data: list[Doc] = _detect(cls, "", side="impl", reverse=False)
            new_doc: str = self.merge(proto_data, impl_data)

            _inject(cls, new_doc, [*proto_data, *impl_data])

            for attr_name in _t.get_protocol_members(protocol):
                target: object | None = _local(cls, attr_name)
                if target is None:
                    continue
                proto_data = _detect(
                    protocol, attr_name, side="proto", reverse=True
                )
                impl_data = _detect(cls, attr_name, side="impl", reverse=True)
                new_doc = self.merge(proto_data, impl_data)
                _inject(target, new_doc, [*proto_data, *impl_data])

            return cls

        return portlinker

    def __call__1[C, P](self, protocol: type[P], /) -> PortLinker[C, P]:
        def portlinker(cls: type[C & P]) -> type[C]:

            # --- 1. Deduplication / Tracking ---
            existing_links: frozenset[type] = getattr(
                cls, "__portlinks__", frozenset()
            )
            if protocol in existing_links:
                return cls  # Pipeline already processed this exact protocol for this class

            # --- 2. Process Class Scope ---
            proto_docs = _collect_fragments(protocol, None, "proto")
            impl_docs = _collect_fragments(cls, None, "impl")

            if proto_docs or impl_docs:
                merged_class_doc = self._merge(
                    proto_docs, impl_docs, is_class=True
                )
                _inject(cls, merged_class_doc)

            # --- 3. Process Attribute Scope ---
            for attr_name in _t.get_protocol_members(protocol):
                proto_attr_docs = _collect_fragments(
                    protocol, attr_name, "proto"
                )
                impl_attr_docs = _collect_fragments(cls, attr_name, "impl")

                if proto_attr_docs or impl_attr_docs:
                    # Get actual implementation attribute to inject into
                    target_attr = _reflect(cls, attr_name)
                    if target_attr:
                        # Extract underlying func if it's a static/classmethod for injection
                        inject_target = _reflect(target_attr)
                        merged_attr_doc = self._merge(
                            proto_attr_docs, impl_attr_docs, is_class=False
                        )
                        _inject(inject_target, merged_attr_doc)

            # --- 4. Finalize State ---
            try:
                cls.__portlinks__ = existing_links | frozenset([protocol])
            except TypeError:
                pass

            return cls

        return portlinker

    def __call__2[C, P](self, protocol: type[P]) -> PortLinker[C, P]:
        def decorator(cls: type[C]) -> type[C]:
            # === Class docstring ===
            class_docs = self._collect_class_docs(protocol, cls)
            if class_docs:
                final = self._merge(class_docs)
                self._inject_class_doc(cls, final)

            # === Attribute docstrings ===
            for attr_name in _t.get_protocol_members(protocol):
                attr_docs = self._collect_attr_docs(protocol, cls, attr_name)
                if attr_docs:
                    final = self._merge(attr_docs)
                    self._inject_attr_doc(cls, attr_name, final, attr_docs)

            # Record history (for future dedup / debugging)
            self._record_links(cls, protocol)
            return cls

        return decorator

    def _collect_class_docs(self, protocol: type, impl: type) -> list[Doc]:
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

    def _record_links(self, cls: type, protocol: type) -> None:
        """Lightweight history on the class."""
        links = getattr(cls, "__port_links__", set())
        links.add(protocol)
        # Use object.__setattr__ in case someone makes the class frozen later
        try:
            cls.__port_links__ = links
        except AttributeError, TypeError:
            pass

    @staticmethod
    def _attach_history(target: object, fragments: list[Doc]) -> None:
        """Attach contributor info directly on the function/object."""
        if not hasattr(target, "__portlink_sources__"):
            try:
                target.__portlink_sources__ = set()
            except AttributeError, TypeError:
                return

        for f in fragments:
            target.__portlink_sources__.add((f.side, f.owner))

    def _collect_attr_docs(
        self, protocol: type, impl: type, attr_name: str
    ) -> list[Doc]:
        docs: list[Doc] = []
        seen: set[tuple] = set()

        # Protocol side (earliest protocol first for attributes)
        for base in reversed(protocol.__mro__):  # reversed = earliest first
            if base in (object, _t.Protocol, _t.Generic):
                continue
            attr = _reflect(base, attr_name)
            if attr:
                text = _detect(attr)
                if text:
                    dd = Doc("proto", base, attr_name, text)
                    if dd.key() not in seen:
                        seen.add(dd.key())
                        docs.append(dd)

        # Implementation side (definition order in MRO)
        for base in impl.__mro__:
            if base in (object, _t.Protocol, _t.Generic):
                continue
            if attr_name in base.__dict__:
                attr = _reflect(base, attr_name)
                if attr:
                    text = _detect(attr)
                    if text:
                        dd = Doc("impl", base, attr_name, text)
                        if dd.key() not in seen:
                            seen.add(dd.key())
                            docs.append(dd)

        return docs

    def _link(self, protocol: type, cls: type) -> None:
        """Process one @portlink() decoration (class + all members)."""
        if not hasattr(cls, "__port_links__") or not isinstance(
            cls.__port_links__, frozenset
        ):
            cls.__port_links__ = frozenset()

        # Class-level docstring (latest protocol first)
        if (protocol, None) not in cls.__port_links__:
            fragments = _collect_fragments(protocol, cls, attr_name=None)
            if fragments:
                _safe_inject(cls, self.merge(fragments, is_class_doc=True))
            cls.__port_links__ |= {(protocol, None)}

        # Per-attribute docs (earliest protocol first for methods)
        for name in _t.get_protocol_members(protocol):
            key = (protocol, name)
            if key in cls.__port_links__:
                continue

            fragments = _collect_fragments(protocol, cls, attr_name=name)
            if fragments:
                target = _reflect(cls, name)
                if target is not None:
                    _safe_inject(
                        target, self.merge(fragments, is_class_doc=False)
                    )

            cls.__port_links__ |= {key}


portlink = PortLink()  # TARGET: the main object


#  LINE: -- Internal Logic -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LinkSpec:
    name = FixTypeField[str](types=str)
    skip = FixTypeField[frozenset[type]](types=frozenset)

    def __init__(self, *, name: str, skip: frozenset[type]) -> None:
        self.name: str = name
        self.skip: frozenset[type] = skip

    def ignores(self, base: type) -> bool:
        return base in self.skip


_SKIP: frozenset[type] = frozenset({object, _t.Protocol, _t.Generic})

spec = LinkSpec(name="Settings", skip=_SKIP)


def _local(cls: type, name: str, /) -> object | None:
    """Locally defined attr only — never an inherited function object."""
    if name not in cls.__dict__:
        return None
    return _reflect(cls.__dict__[name])


def _payload(base: type, name: str, /) -> object | None:
    if not name:
        return base
    if name not in base.__dict__:
        return None
    return _reflect(base.__dict__[name])


def _reflect(cls: type, attr_name: str, /) -> _t.Any | None:
    # IDEA: _scan?
    match attr := cls.__dict__.get(attr_name):
        case classmethod() | staticmethod():
            return attr.__func__
        case property() | _cached_property():
            return attr
        case _ if callable(attr):
            return attr
        case _:
            return None


def _raw_doc(payload: object, name: str, /) -> str:
    if not name:
        raw: object | None = payload.__dict__.get("__doc__")
    else:
        raw = getattr(payload, "__doc__", None)
    return _cleandoc(raw) if isinstance(raw, str) and raw else ""


def _get_original_doc(target: _t.Any) -> str:
    if hasattr(target, "__portlink_orig_doc__"):
        return target.__portlink_orig_doc__

    doc = getattr(target, "__doc__", None)
    return _cleandoc(doc) if doc else ""


def _collect_fragments(
    cls: type, attr_name: str | None, side: _t.Literal["port", "plug"]
) -> list[Doc]:
    fragments: list[Doc] = []

    for base in cls.__mro__:
        if base in (object, type, _t.Protocol, _t.Generic):
            continue

        # Target is either the class itself or an attribute in its __dict__
        target = base if attr_name is None else base.__dict__.get(attr_name)

        if target is None:
            continue

        text = _get_original_doc(target)
        if text:
            fragments.append(Doc(side, base, text))

    return fragments


def _own_text(base: type, name: str, side: _Side, payload: object, /) -> str:
    """Original fragment for this defining class. Never a previously merged blob."""
    links: object = getattr(payload, "__links__", None)
    if isinstance(links, frozenset):
        for item in links:
            if (
                isinstance(item, Doc)
                and item.owner is base
                and item.name == name
                and item.side == side
            ):
                return item.text
        return ""
    return _raw_doc(payload, name)


def _extract_clean_doc(target: _t.Any, /) -> str:  #
    """Scan for Docstring"""
    doc: str | None = getattr(target, "__doc__", None)
    return _cleandoc(doc) if doc else ""


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
    side: _Side,
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


def _safe_inject(target: _t.Any, doc: str) -> bool:
    """Best-effort injection that works for classes, functions, properties, etc."""
    try:
        # Prefer writing into __dict__ when possible (avoids descriptor __set__)
        if hasattr(target, "__dict__") and isinstance(target.__dict__, dict):
            target.__dict__["__doc__"] = doc
            return True

        # Common descriptor cases
        if isinstance(target, property) and target.fget is not None:
            target.fget.__doc__ = doc
            return True
        if hasattr(target, "__func__"):  # classmethod / staticmethod
            target.__func__.__doc__ = doc
            return True

        target.__doc__ = doc
        return True
    except AttributeError, TypeError:
        return False


def _attach(target: _t.Any, doc: str, /) -> None:
    try:  # LATER: swap names inject/attach
        target.__doc__ = doc
    except AttributeError, TypeError:
        pass


def _attach_links(cls: _t.Any, links: frozenset[Doc], /) -> None:
    try:  # LATER: swap names inject/attach
        cls.__portlinks__ = links
        object.__setattr__(cls, "__links__", links)
    except AttributeError, TypeError:
        pass


def _inject(target: _t.Any, new_doc: str) -> None:
    """Safely inject the new docstring and preserve the original."""
    # 1. Preserve original state to protect against stacked decorators
    if not hasattr(target, "__portlink_orig_doc__"):
        original_doc = getattr(target, "__doc__", None)
        try:
            # We use setattr in case it's a class or standard object
            target.__portlink_orig_doc__ = (
                _cleandoc(original_doc) if original_doc else ""
            )
        except AttributeError, TypeError:
            pass  # Immutable object (like some C-extensions or slots without dict)

    # 2. Inject new doc
    try:
        if isinstance(target, type):
            target.__doc__ = new_doc
        else:
            target.__doc__ = new_doc
    except AttributeError, TypeError:
        pass


def ___inject(cls: type, attr_name: str, data) -> None:
    """Safely attach the doc only if the attribute is explicitly on THIS class."""
    if attr_name not in cls.__dict__:
        return  # It is inherited. Do not mutate the base class descriptor.

    object.__setattr__(cls, attr_name, data)


def _inject(cls: type, attr_name: str, doc: str) -> None:
    """Safely attach the doc only if the attribute is explicitly on THIS class."""
    if attr_name not in cls.__dict__:
        return  # It is inherited. Do not mutate the base class descriptor.

    _attach(cls if attr_name == "__doc__" else cls.__dict__[attr_name], doc)


def _inject(target: object, doc: str, data: _t.Sequence[Doc], /) -> None:
    """Stamp ``__doc__`` and ``__links__``. Worst case: nothing changes."""
    if not doc:
        return
    links: frozenset[Doc] = frozenset(data)
    if getattr(target, "__links__", None) == links:
        return
    try:
        target.__doc__ = doc  # type: ignore[attr-defined]
    except AttributeError, TypeError:
        return
    try:
        object.__setattr__(target, "__links__", links)
    except AttributeError, TypeError:
        try:
            target.__links__ = links  # type: ignore[attr-defined]
        except AttributeError, TypeError:
            return


def _find_injection_target(cls: type, attr_name: str) -> _t.Any | None:
    if attr_name in cls.__dict__:
        target = _reflect(cls, attr_name)
        _stash_raw_doc(target)
        return target

    for base in cls.__mro__:
        if spec.ignores(base):
            continue
        if attr_name in base.__dict__:
            target = _reflect(cls, attr_name)
            _stash_raw_doc(target)
            return target

    return None


def _inject(target: _t.Any, doc: str, /) -> bool:
    """Safely apply docstring without triggering descriptor __set__ methods."""
    if target is None:
        return False
    try:
        target.__doc__ = doc
        return True
    except AttributeError, TypeError:
        return False


def _extract_origins(
    cls: type, attr_name: str, side: _t.Literal["port", "plug"]
) -> _t.Iterator[Doc]:
    """Walk MRO. Yield Doc. Use __portlinks__ if available to avoid raw parsing."""
    for base in cls.__mro__:
        if base in (object, type, _t.Protocol, _t.Generic):
            continue

        if portlinks := base.__dict__.get("__portlinks__"):
            if attr_name in portlinks:
                yield from portlinks[attr_name]
                continue

        if attr_name not in base.__dict__:
            continue

        target: _t.Any = (
            base if attr_name == "__doc__" else base.__dict__[attr_name]
        )

        doc = getattr(target, "__doc__", None)
        if text := (_cleandoc(doc) if doc else ""):
            yield Doc(side, base, text)


#  LINE: -- Possible Improvements -- -- - -- -- - -- -- - -- -- - -- -- - -- --


if _t.TYPE_CHECKING:
    import enum as _e

    @_dataclass(frozen=True, slots=True)
    class _Doc:
        source: type  # the class/protocol where it was defined
        attr: str  # the attribute name
        doc: str
        origin: str  # "protocol" | "implementation"

    class Event(_e.Enum):
        PROTO_DIRECT = _e.auto()
        PROTO_BASE = _e.auto()
        IMPL_DIRECT = _e.auto()
        IMPL_BASE = _e.auto()

    class DocBuilder:
        def __init__(self):
            self.parts: list[str] = []
            self.seen: set[str] = set()
            self.last_event: Event | None = None

        def add(self, fragment: _Doc, event: Event) -> None:
            if fragment.doc in self.seen:
                return
            # rules based on event sequence
            if (
                event is Event.PROTO_BASE
                and self.last_event is Event.PROTO_DIRECT
            ):
                # protocol overrode its own base — maybe skip or mark
                pass
            self.parts.append(fragment.doc)
            self.seen.add(fragment.doc)
            self.last_event = event
