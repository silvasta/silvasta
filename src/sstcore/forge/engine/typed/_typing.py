"""
Extract Type Information from Protocols and Classes for Stub Generation

- Execute functional stack together with Class Builder and Meta Constructors


                      DependencyLevel.sstcore.forge.engine.typed[0]
"""

__all__: list[str] = [
    "is_protocol",
    "extract_members",
    "render_signature",
    "render_protocol_stub",
    "ForgeTyper",
]

import inspect
from collections.abc import Callable, Sequence
from typing import (
    Any,
    Generic,
    Literal,
    Protocol,
    get_overloads,
    get_type_hints,
)

type ProtoType = type
type AttrName = str
type RawObject = object
type PublicMember = tuple[AttrName, RawObject, AttrKind]


type AttrKind = Literal["property", "method", "attribute"]
# EXTRACT: maybe? but then send from port
type TypeHints = dict[str, Any]
type OverLoads = Sequence[Callable[..., Any]]

#  LINE: -- Detection -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def is_protocol(cls: type) -> bool:
    """Return True if cls is a Protocol subclass with the flag set."""
    return issubclass(cls, Protocol) and getattr(cls, "_is_protocol", False)


def is_private_not_calling(attr: str) -> bool:
    exclude: set[str] = {"__call__", "__getitem__"}
    return attr.startswith("_") and attr not in exclude


def is_typing_meta_blueprint(cls: type) -> bool:
    return cls in (object, Protocol, Generic)


#  LINE: -- Extraction -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def extract_members(cls: type) -> list[PublicMember]:
    """Walk cls.__mro__ bottom-up and collect public member"""

    hints: TypeHints = get_type_hints(cls, include_extras=True)
    seen: set[str] = set()
    members: list[PublicMember] = []

    for base in reversed(cls.__mro__):
        if is_typing_meta_blueprint(cls=base):
            continue
        for name, raw in base.__dict__.items():  # LATER: labor._dict
            if is_private_not_calling(attr=name) or name in seen:
                continue
            seen.add(name)

            if kind := classify_member(name, raw, hints):
                members.append((name, raw, kind))

    return members


def classify_member(
    name: str, raw: Any, hints: dict[str, Any]
) -> AttrKind | None:
    match raw:
        case property():
            return "property"
        case Callable():
            return "method"
        case _:
            if name in hints:
                return "attribute"
    return None


#  LINE: -- Rendering -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _format_annotation(type_annot: Any) -> str:
    """Best-effort string representation of a type annotation."""
    if type_annot is inspect.Parameter.empty:
        return "Any"
    if hasattr(type_annot, "__name__"):
        return type_annot.__name__
    return str(type_annot).replace("typing.", "")


def render_signature(fn: Any, name: str) -> list[str]:
    """Render a single method (including @overload variants) as stub lines."""
    lines: list[str] = []
    overloads: OverLoads = get_overloads(fn)
    targets: OverLoads | list[Any] = overloads or [fn]

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

        params: list[str] = []
        for p_name, param in sig.parameters.items():
            # CHECK: match/case for more clarity?
            ann = _format_annotation(param.annotation)
            if param.default is not inspect.Parameter.empty:
                params.append(f"{p_name}: {ann} = ...")
            elif param.kind == inspect.Parameter.VAR_POSITIONAL:
                params.append(f"*{p_name}: {ann}")
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                params.append(f"**{p_name}: {ann}")
            else:
                params.append(f"{p_name}: {ann}")

        ret = _format_annotation(sig.return_annotation)
        lines.append(f"    def {name}({', '.join(params)}) -> {ret}: ...")
    return lines


def render_protocol_stub(cls: type, *, name: str = "") -> str:
    """
    Render Protocol or Regular Class to Stub File

    - Walk MRO, handle @property, @overload, and type hints
    - include_extras=True preserves Annotated etc...
    """

    hints: TypeHints = get_type_hints(cls, include_extras=True)
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


class ForgeTyper:
    # TODO: Naming:
    # - Rating from 1-5
    # - 1 ClassAnalyzer
    # - 3 ProtoAnalyzer
    # - 3 ProtoScanner
    # - 5 ProtoMixer
    # - 2 CompositionAnalyzer
    # - 4 MixAnalyzer
    # - 5 MixInspector
    # - 3 ConstructionTyper
    # - 4 ForgeTyper
    # - 4 DynamicAnnotator
    """
    Functional adapter that bridges protocol extraction to the Typer protocol.

    Each classmethod accepts a protocol or class and returns ready-to-write
    stub text.  This is the primary entry point for forge.engine consumers
    that need typed output without depending on util.write.
    """

    @classmethod
    def draw(cls, source: type, *, name: str = "") -> str:
        """Render a full class stub from a Protocol or regular class."""
        return render_protocol_stub(source, name=name)

    @classmethod
    def members(cls, source: type) -> list[PublicMember]:
        """Expose extracted members for downstream consumers (Builder, Meta)."""
        return extract_members(source)
