"""
process

.
"""

from inspect import cleandoc as _cleandoc

from .data import Doc
from .define import DocMerger

#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

# TODO: machine


def concat_merger(ports: list[Doc], plugs: list[Doc], is_class: bool) -> str:
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
    ordered_ports = ports if is_class else list(reversed(ports))
    ordered_plugs = plugs if is_class else list(reversed(plugs))

    _add_fragments(ordered_ports, "Definitions from the Port")
    _add_fragments(ordered_plugs, "Implementations")

    return "\n".join(lines).strip()


x: DocMerger = concat_merger


def default_merge(
    ports: list[Doc],
    plugs: list[Doc],
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

    filtered_ports: list[Doc] = [
        p
        for p in ports
        if p.text not in seen_texts and not seen_texts.add(p.text)
    ]
    if filtered_ports:
        p_lines: list[str] = ["{Definitions from the Port}"]
        for p in filtered_ports:
            p_lines.append(f"[{p.owner.__name__}]\n{p.text}")
        sections.append("\n\n".join(p_lines))

    filtered_plugs: list[Doc] = [
        i
        for i in plugs
        if i.text not in seen_texts and not seen_texts.add(i.text)
    ]
    if filtered_plugs:
        i_lines: list[str] = ["{Implementations}"]
        for i in filtered_plugs:
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


def __default_merge(ports: _Docs, plugs: _Docs, /, joint: str = "") -> str:
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
    rest_impl: _Docs = plugs

    if ports:
        _lead_source, rest_proto = ports[:1], ports[1:]
    else:
        _lead_source, rest_proto = plugs[:1], ()
        rest_impl = plugs[1:]

    titled_proto: list[str] = take(rest_proto, titled=True)
    if titled_proto:
        chunks.append("{Definitions from the Port}")
        chunks.extend(titled_proto)

    titled_impl: list[str] = take(rest_impl, titled=True)
    if titled_impl:
        chunks.append(joint.strip() or "{Implementations}")
        chunks.extend(titled_impl)

    return "\n\n".join(chunks)
