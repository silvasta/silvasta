"""
Write Stubs from Protocols and Type Meta-, Class- and Instance

-
"""

__all__: list[str] = [
    "ForgeTyper",
]

# NEXT: split and re-assemble this until valuable material is collected

import inspect
from typing import Generic, Protocol, get_overloads, get_type_hints

from ...brick.labor import funcname


def fmt(*args, **kwargs):
    raise NotImplementedError


def fmt_sig(*args, **kwargs):
    raise NotImplementedError


type ProtoType = type


class GreeterProto(Protocol):
    def greet(self, name: str) -> str: ...
    @property
    def language(self) -> str: ...


class ForgeTyper:
    @classmethod
    def draw(cls, name: str, proto: ProtoType) -> str:
        ...
        # Извлекаем методы и атрибуты из Protocol
        # members = cls._extract_protocol_members(proto)
        # # Генерируем класс-стаб
        # return cls._generate_class_stub(name, members)


class ProtoTyper:
    @classmethod
    def draw(cls, protocol: ProtoType, name: str = "") -> str:
        name = name or protocol.__name__.replace("Protocol", "Stub")
        hints = get_type_hints(protocol)
        lines = [f"class {name}:"]
        for attr, typ in hints.items():
            if attr.startswith("__"):
                continue
            if callable(typ):
                lines.append(
                    f"    def {attr}(self, *args: Any, **kwargs: Any) -> Any: ..."
                )
            else:
                lines.append(f"    {attr}: {funcname(typ, default='Any')}")
        lines.append("    ...")
        return "\n".join(lines)


def is_protocol(cls: type) -> bool:
    return issubclass(cls, Protocol) and getattr(cls, "_is_protocol", False)


def render_protocol(cls: type) -> str:
    hints = get_type_hints(cls, include_extras=True)
    lines = [f"class {cls.__name__}(Protocol):"]
    seen: set[str] = set()

    for base in reversed(cls.__mro__):
        if base in (object, Protocol, Generic):
            continue
        for name, raw in base.__dict__.items():
            if name.startswith("_") and name not in {
                "__call__",
                "__getitem__",
            }:
                continue
            if name in seen:
                continue
            seen.add(name)

            if isinstance(raw, property):
                ret = hints.get(name, "Any")
                lines += [
                    "    @property",
                    f"    def {name}(self) -> {fmt(ret)}: ...",
                ]
                continue

            if not callable(raw):
                if name in hints:
                    lines.append(f"    {name}: {fmt(hints[name])}")
                continue

            overloads = get_overloads(raw)
            targets = overloads or [raw]
            for fn in targets:
                if overloads:
                    lines.append("    @overload")
                sig = inspect.signature(fn)
                lines.append(f"    def {name}{fmt_sig(sig)}: ...")

    if len(lines) == 1:
        lines.append("    ...")
    return "\n".join(lines)


class DummyProtocol(Protocol):
    def execute(self, target: str) -> bool: ...
    @property
    def name(self) -> str: ...


def extract_protocol_stub(protocol_cls: ProtoType) -> str:
    stub_lines = [f"class {protocol_cls.__name__}:"]

    # 1. Extract Properties / Attributes
    hints = get_type_hints(protocol_cls)
    for attr_name, attr_type in hints.items():
        if not attr_name.startswith("_"):
            # Format nicely using your funcname utility
            stub_lines.append(f"    {attr_name}: {attr_type.__name__}")

    # 2. Extract Methods
    methods = inspect.getmembers(protocol_cls, inspect.isfunction)
    for name, func in methods:
        if name == "__init__":
            continue

        sig = inspect.signature(func)
        # You can reuse your existing _render_param logic here
        stub_lines.append(f"    def {name}{sig}: ...")

    return "\n".join(stub_lines)
