# /home/silvan/sstcore/src/sstcore/forge/engine/_typing.py
"""
Introspect Protocols and Mixins to Synthesize Static Stubs

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "ForgeTyper",
]

import inspect
from collections.abc import Iterator, Sequence
from typing import Any, get_overloads, get_type_hints

from ...brick import reflect
from ...port.annotate import MethodSpec, ProtocolSpec
from ...port.annotate import stub_types as _stub
from ...port.link import portlink
from ...port.shape import Typer

PROTO_FILTER = reflect.AttrFilter.protocol(
    exclude={
        "__subclasshook__",
        "__init__",
        "__new__",
        "__annotations__",
        "__dict__",
        "__weakref__",
        "__doc__",
        "__module__",
        "_is_protocol",
        "_is_runtime_protocol",
    },
)


# NEXT: sync with _typed_well


def format_clsname(target: _stub.ProtoType, name: str | None = None, /) -> str:
    return name or target.__name__


def iter_mro(target: _stub.ProtoType) -> Iterator[_stub.ProtoType]:
    for base in reversed(target.__mro__):
        if reflect.is_typing_generic(base):
            continue
        yield base


def iter_dict(base: _stub.ProtoType, seen) -> Iterator[tuple[str, Any]]:
    for name, member in base.__dict__.items():
        if name in seen or PROTO_FILTER(name):
            continue
        seen.add(name)
        yield name, member


def handle_callable(name, member) -> MethodSpec:
    if overloads := get_overloads(member):
        return MethodSpec(
            name=name,
            signatures=[inspect.signature(fn) for fn in overloads],
            is_overloaded=True,
        )
    else:
        return MethodSpec(
            name=name,
            signatures=[inspect.signature(member)],
            is_overloaded=False,
        )


@portlink(Typer)
class ForgeTyper:
    """Synthesize stub definitions from inspected protocols and schemas."""

    @classmethod
    def draw(cls, target: _stub.ProtoType, clsname: str | None = None) -> str:
        """Draw a complete class stub from a Protocol or Mixin"""
        spec: ProtocolSpec = scan_protocol(target, clsname)
        lines: list[str] = stub_protocol(spec, clsname)
        return "\n".join(lines)

    @classmethod
    def merge_and_draw(cls, targets: Sequence[type], target_name: str) -> str:
        """Compose multiple protocols/mixins into a unified stub interface."""
        merged_attrs: dict[str, type] = {}
        merged_props: dict[str, type] = {}
        merged_methods: dict[str, MethodSpec] = {}

        for target in targets:
            spec = scan_protocol(target)
            merged_attrs.update(spec.attributes)
            merged_props.update(spec.properties)
            merged_methods.update(spec.methods)

        composite = ProtocolSpec(
            name=target_name,
            attributes=merged_attrs,
            properties=merged_props,
            methods=merged_methods,
        )
        lines: list[str] = stub_protocol(composite, target_name)
        return "\n".join(lines)


def handle_property(name, member, hints):
    return hints.get(name, member.fget.__annotations__.get("return", Any))


def format_type(typ: Any) -> str:
    if typ is None or typ is type(None):
        return "None"
    if hasattr(typ, "__name__"):
        return typ.__name__
    return str(typ).replace("typing.", "")


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def scan_protocol(
    target: type, proto_name: str | None = None, /
) -> ProtocolSpec:
    """Detect all attributes and annotations on the Protocol"""

    spec = ProtocolSpec(name=format_clsname(target, proto_name))
    hints: dict[str, Any] = get_type_hints(target, include_extras=True)
    seen: set[str] = set()

    for base in iter_mro(target):
        for name, member in iter_dict(base, seen):
            if isinstance(member, property):
                spec.properties[name] = handle_property(name, member, hints)
                continue
            if callable(member):
                spec.methods[name] = handle_callable(name, member)
                continue
            if name in hints:
                spec.attributes[name] = hints[name]

    return spec


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def stub_protocol(
    spec: ProtocolSpec, clsname: str | None = None, /
) -> list[str]:
    """Type all attributes and annotations of the Protocol for Stub"""

    lines: list[str] = []

    lines.append(write_class(clsname or spec.name))

    if body := write_body(spec):
        lines.extend(body)
    else:
        lines.append(write_empty_body())

    return lines


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def write_body(spec: ProtocolSpec) -> list[str]:
    """Separate Pipeline from Rendering"""

    lines: list[str] = []

    for attr, attr_type in spec.attributes.items():
        lines.append(write_attr(attr, attr_type))

    for prop, prop_type in spec.properties.items():
        lines.append(write_prop_deco())
        lines.append(write_prop_line(prop, prop_type))

    for method in spec.methods.values():
        for sig in method.signatures:
            if method.is_overloaded:
                lines.append(write_overload())
            lines.append(write_method(method, sig))

    return lines


def write_class(name):
    return f"class {name}:"


def write_empty_body():
    return "    ..."


def write_attr(attr, attr_type):
    return f"    {attr}: {format_type(attr_type)}"


def write_prop_deco():
    return "    @property"


def write_prop_line(prop, prop_type):
    return f"    def {prop}(self) -> {format_type(prop_type)}: ..."


def write_overload():
    return "    @overload"


def write_method(method, sig):
    return f"    def {method.name}{str(sig)}: ..."
