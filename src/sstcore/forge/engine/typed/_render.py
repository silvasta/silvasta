"""
Extract Type Information from Protocols and Classes for Stub Generation

- Execute functional stack together with Class Builder and Meta Constructors


                      DependencyLevel.sstcore.forge.engine.typed[0]
"""

__all__: list[str] = [
    "render_signature",
    "render_protocol_stub",
]


import inspect
from collections.abc import Mapping
from typing import Any, get_overloads, get_type_hints

from . import _types as _t
from ._detect import is_protocol
from ._extract import extract_members


def _format_annotation(type_annot: Any) -> str:
    # MOVE: machine
    """Best-effort string representation of a type annotation."""
    if type_annot is inspect.Parameter.empty:
        return "Any"
    if hasattr(type_annot, "__name__"):
        return type_annot.__name__
    return str(type_annot).replace("typing.", "")


def render_signature(fn: Any, name: str) -> list[str]:
    """Render a single method (including @overload variants) as stub lines."""
    lines: list[str] = []
    overloads: _t.OverLoads = get_overloads(fn)
    targets: _t.OverLoads | list[Any] = overloads or [fn]

    for fn_target in targets:
        # EXTRACT: oveload mechanism
        if overloads:
            lines.append("    @overload")
        try:
            sig = inspect.signature(fn_target)
        except ValueError, TypeError:
            lines.append(
                f"    def {name}(self, *args: Any, **kwargs: Any) -> Any: ..."
            )
            continue

        # EXTRACT:
        params: list[str] = []
        for p_name, param in sig.parameters.items():
            ann = _format_annotation(param.annotation)
            if param.default is not inspect.Parameter.empty:
                params.append(f"{p_name}: {ann} = ...")
            elif param.kind == inspect.Parameter.VAR_POSITIONAL:
                params.append(f"*{p_name}: {ann}")
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                params.append(f"**{p_name}: {ann}")
            else:
                params.append(f"{p_name}: {ann}")
                # EXTRACT:

        ret = _format_annotation(sig.return_annotation)
        lines.append(f"    def {name}({', '.join(params)}) -> {ret}: ...")
    return lines


def render_protocol_stub(cls: type, *, name: str = "") -> str:
    """
    Render Protocol or Regular Class to Stub File

    - Walk MRO, handle @property, @overload, and type hints
    - include_extras=True preserves Annotated etc...
    """

    hints: _t.TypeHints = get_type_hints(cls, include_extras=True)
    from_protocol: str = "(Protocol)" if is_protocol(cls) else ""
    lines: list[str] = [f"class {name or cls.__name__}{from_protocol}:"]

    for member_name, raw, kind in extract_members(cls):
        match kind:
            case "property":
                ret: str = _format_annotation(hints.get(member_name, Any))
                lines += [  # EXTRACT: annotoolbox?
                    "    @property",
                    f"    def {member_name}(self) -> {ret}: ...",
                ]
            case "method":  # EXTRACT: to machinery
                lines += render_signature(raw, member_name)

            case "attribute":
                ann: str = _format_annotation(hints[member_name])
                lines.append(f"    {member_name}: {ann}")

    if len(lines) == 1:
        lines.append("    ...")
    lines.append("")

    return "\n".join(lines)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def render_class_stub(name: str, members: dict[str, Any]) -> str:
    lines = [f"class {name}:"]
    for attr, value in members.items():
        if callable(value):
            try:
                sig = inspect.signature(value)
                lines.append(f"    def {attr}{sig}: ...")
            except ValueError, TypeError:
                lines.append(
                    f"    def {attr}(self, *args: Any, **kwargs: Any) -> Any: ..."
                )
        else:
            lines.append(
                f"    {attr}: {getattr(value, '__name__', str(value))}"
            )
    if len(lines) == 1:
        lines.append("    ...")
    return "\n".join(lines)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def synthesize_fluent_code(
    prefix: str, schema: Mapping[str, list[str]], call_signature: str
) -> str:
    lines = [
        f"# Auto-generated fluent stubs for {prefix}",
        "from typing import Self, Any",
        "",
        f"class {prefix}Empty:",
    ]

    # 1. State empty: all layers available
    for _layer_name, attributes in schema.items():
        for attr in attributes:
            lines.append("    @property")
            lines.append(f"    def {attr}(self) -> {prefix}Active: ...")

    # 2. Add Callable stub to direct Empty state
    lines.append(f"    def __call__{call_signature}: ...")
    lines.append("")

    # 3. State Active: subsequent calls
    lines.append(f"class {prefix}Active:")
    for _layer_name, attributes in schema.items():
        for attr in attributes:
            lines.append("    @property")
            lines.append(f"    def {attr}(self) -> Self: ...")

    lines.append(f"    def __call__{call_signature}: ...")
    lines.append("")
    return "\n".join(lines)
