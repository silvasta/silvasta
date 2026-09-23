"""Extract Protocols / classes into .pyi text. No paths, no I/O.

DependencyLevel[1]
"""

from __future__ import annotations

__all__ = [
    "protocol_members",
    "format_annotation",
    "format_signature",
    "render_class",
    "draw_protocol",
]

import inspect
from collections.abc import Sequence
from types import FunctionType, UnionType
from typing import (
    Any,
    Generic,
    Protocol,
    Union,
    get_args,
    get_origin,
    get_overloads,
    get_type_hints,
)

from . import _classify as _c

_SKIP_BASES = frozenset({object, Protocol, Generic})
_KEEP_DUNDER = frozenset({"__call__", "__getitem__", "__iter__", "__len__"})


def format_annotation(hint: object) -> str:
    # EXTRACT: machine
    if hint is inspect.Signature.empty or hint is inspect.Parameter.empty:
        return "Any"
    if hint is type(None):
        return "None"
    if hint is Any:
        return "Any"
    if isinstance(hint, str):
        return hint

    # EXTRACT:
    origin = get_origin(hint)
    if origin is Union or origin is UnionType or isinstance(hint, UnionType):
        parts = [format_annotation(a) for a in get_args(hint)]
        if "None" in parts:
            rest = [p for p in parts if p != "None"]
            inner = rest[0] if len(rest) == 1 else " | ".join(rest)
            return f"{inner} | None" if rest else "None"
        return " | ".join(parts)
    # EXTRACT:
    if origin is not None:
        args = ", ".join(format_annotation(a) for a in get_args(hint))
        return (
            f"{format_annotation(origin)}[{args}]"
            if args
            else format_annotation(origin)
        )
    # EXTRACT:

    if isinstance(hint, type):
        if hint.__module__ in {
            "builtins",
            "typing",
            "collections.abc",
            "types",
        }:
            return hint.__name__
        # EXTRACT:
        return f"{hint.__module__.split('.')[-1]}.{hint.__name__}"
    return getattr(hint, "__name__", repr(hint))


def format_signature(
    sig: inspect.Signature, *, skip_first: bool = False
) -> str:
    # EXTRACT:
    params: list[str] = []
    items = list(sig.parameters.values())
    if skip_first and items:
        first, items = items[0], items[1:]
        params.append(first.name)

    # EXTRACT:
    for p in items:
        piece = p.name
        if p.kind is inspect.Parameter.VAR_POSITIONAL:
            piece = f"*{p.name}"
        elif p.kind is inspect.Parameter.VAR_KEYWORD:
            piece = f"**{p.name}"
        elif p.kind is inspect.Parameter.KEYWORD_ONLY and not any(
            x.startswith("*") for x in params
        ):
            params.append("*")
            piece = p.name

        # EXTRACT:
        if p.annotation is not inspect.Parameter.empty:
            piece = f"{piece}: {format_annotation(p.annotation)}"
        if p.default is not inspect.Parameter.empty:
            piece = f"{piece} = ..."
        params.append(piece)

    ret = format_annotation(sig.return_annotation)
    return f"({', '.join(params)}) -> {ret}"


def _hint_map(cls: type) -> dict[str, object]:
    # EXTRACT:
    try:
        return get_type_hints(cls, include_extras=True)
    except Exception:
        return dict(getattr(cls, "__annotations__", {}))


def protocol_members(cls: type) -> tuple[_c.ProtoMember, ...]:
    """MRO walk: properties, overloads, annotated attrs. First definition wins."""
    hints = _hint_map(cls)
    seen: set[str] = set()
    out: list[_c.ProtoMember] = []

    # EXTRACT:
    for base in reversed(cls.__mro__):
        if base in _SKIP_BASES:
            continue
        for name, raw in base.__dict__.items():
            if name in seen:
                continue
            if name.startswith("_") and name not in _KEEP_DUNDER:
                continue
            seen.add(name)

            # EXTRACT:
            if isinstance(raw, property):
                out.append(
                    _c.ProtoMember(
                        name=name,
                        kind=_c.MemberKind.PROP,
                        annotation=format_annotation(hints.get(name, Any)),
                    )
                )
                continue

            # EXTRACT:
            if isinstance(
                raw, (FunctionType, classmethod, staticmethod)
            ) or callable(raw):
                fn = (
                    raw.__func__
                    if isinstance(raw, (classmethod, staticmethod))
                    else raw
                )
                targets = list(get_overloads(fn)) or [fn]
                sigs = tuple(
                    format_signature(inspect.signature(fn_i), skip_first=True)
                    for fn_i in targets
                )
                out.append(
                    _c.ProtoMember(
                        name=name, kind=_c.MemberKind.METHOD, signatures=sigs
                    )
                )
                continue

            # EXTRACT:
            if name in hints:
                out.append(
                    _c.ProtoMember(
                        name=name,
                        kind=_c.MemberKind.ATTR,
                        annotation=format_annotation(hints[name]),
                    )
                )
    return tuple(out)


def render_class(
    name: str,
    members: Sequence[_c.ProtoMember],
    *,
    bases: tuple[str, ...] = (),
) -> str:
    head = f"class {name}({', '.join(bases)}):" if bases else f"class {name}:"
    lines = [head]
    if not members:
        lines.append("    ...")
        return "\n".join(lines)

        # EXTRACT:
    for m in members:
        match m.kind:
            case _c.MemberKind.ATTR:
                lines.append(f"    {m.name}: {m.annotation}")

            case _c.MemberKind.PROP:
                lines += [
                    "    @property",
                    f"    def {m.name}(self) -> {m.annotation}: ...",
                ]

            case _c.MemberKind.METHOD:
                multi = len(m.signatures) > 1
                for sig in m.signatures:
                    if multi:
                        lines.append("    @overload")
                    lines.append(f"    def {m.name}{sig}: ...")
    return "\n".join(lines)


def draw_protocol(protocol: type, *, name: str = "") -> str:
    # EXTRACT: name generation
    stub_name = (
        name
        or protocol.__name__.removesuffix("Protocol").removesuffix("Proto")
        or protocol.__name__
    )
    return render_class(stub_name, protocol_members(protocol))
