"""
Extract Type Information from Protocols and Classes for Stub Generation

- Execute functional stack together with Class Builder and Meta Constructors


                      DependencyLevel.sstcore.forge.engine.typed[0]
"""

__all__: list[str] = [
    "extract_members",
]


import inspect
from typing import Any, get_type_hints

from . import _types as _t
from ._classify import classify_member
from ._detect import is_private_not_calling, is_typing_meta_blueprint


def extract_protocol_stub(protocol: type, name: str | None = None) -> str:
    """Lightweight extraction for quick stub generation."""
    name = name or protocol.__name__.replace("Protocol", "Empty")
    hints = get_type_hints(protocol)
    lines = [f"class {name}:"]

    # EXTRACT: here the core
    for attr, typ in hints.items():
        if attr.startswith("_"):
            continue
        if callable(typ):
            lines.append(
                f"    def {attr}(self, *args: Any, **kwargs: Any) -> Any: ..."
            )
        else:
            lines.append(f"    {attr}: {getattr(typ, '__name__', 'Any')}")
    lines.append("    ...")
    # EXTRACT: here the core

    return "\n".join(lines)


def extract_members(cls: type) -> list[_t.PublicMember]:
    """Walk cls.__mro__ bottom-up and collect public member"""

    hints: _t.TypeHints = get_type_hints(cls, include_extras=True)
    seen: set[str] = set()
    members: list[_t.PublicMember] = []

    # EXTRACT: here the core
    for base in reversed(cls.__mro__):
        if is_typing_meta_blueprint(cls=base):
            continue
        for name, raw in base.__dict__.items():  # LATER: labor._dict
            if is_private_not_calling(attr=name) or name in seen:
                continue
            seen.add(name)

            if kind := classify_member(name, raw, hints):
                members.append((name, raw, kind))
    # EXTRACT: here the core
    return members


def extract_call_signature(call_func: Any) -> str:
    sig = inspect.signature(call_func)
    # WARN:  Drop the first argument ('state') which is handled internally
    # - only for Stacking!
    params = list(sig.parameters.values())
    trimmed_params = params[1:] if params else []
    new_sig = sig.replace(parameters=trimmed_params)
    return str(new_sig)
