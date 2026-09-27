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
    # "PortLinker",
    # "DocMerger",
]

import typing as _t
from dataclasses import dataclass as _dataclass
from dataclasses import replace as _replace

from .data import Doc, DocMerger, PortLinker, ___Doc, _Docs


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
