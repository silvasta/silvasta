# /home/silvan/sstcore/src/sstcore/forge/engine/_typing.py
"""
Introspect Protocols and Mixins to Synthesize Static Stubs

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "ProtocolInspector",
    "ForgeTyper",
    "is_protocol",
]

import inspect
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, get_overloads, get_type_hints


def is_protocol(cls: type) -> bool:
    """Determine whether a given class is a Protocol definition."""
    return issubclass(cls, Protocol) and getattr(cls, "_is_protocol", False)


@dataclass(slots=True, frozen=True)
class MethodSpec:
    name: str
    signatures: list[inspect.Signature]
    is_overloaded: bool = False


@dataclass(slots=True, frozen=True)
class ProtocolSpec:
    name: str
    attributes: dict[str, type] = field(default_factory=dict)
    properties: dict[str, type] = field(default_factory=dict)
    methods: dict[str, MethodSpec] = field(default_factory=dict)


class ProtocolInspector:
    """Extract structural contracts from Protocol and Mixin classes."""

    EXCLUDED_DUNDERS = {
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
    }

    @classmethod
    def inspect(cls, target: type) -> ProtocolSpec:
        hints = get_type_hints(target, include_extras=True)
        attributes: dict[str, type] = {}
        properties: dict[str, type] = {}
        methods: dict[str, MethodSpec] = {}
        seen: set[str] = set()

        for base in reversed(target.__mro__):
            if base in (object, Protocol, Generic):
                continue

            for name, member in base.__dict__.items():
                if name in cls.EXCLUDED_DUNDERS or (
                    name.startswith("_")
                    and not cls._is_whitelisted_dunder(name)
                ):
                    continue
                if name in seen:
                    continue
                seen.add(name)

                if isinstance(member, property):
                    properties[name] = hints.get(
                        name, member.fget.__annotations__.get("return", Any)
                    )
                    continue

                if callable(member):
                    overloads = get_overloads(member)
                    if overloads:
                        sigs = [inspect.signature(fn) for fn in overloads]
                        methods[name] = MethodSpec(
                            name=name, signatures=sigs, is_overloaded=True
                        )
                    else:
                        methods[name] = MethodSpec(
                            name=name,
                            signatures=[inspect.signature(member)],
                            is_overloaded=False,
                        )
                    continue

                if name in hints:
                    attributes[name] = hints[name]

        return ProtocolSpec(
            name=target.__name__,
            attributes=attributes,
            properties=properties,
            methods=methods,
        )

    @staticmethod
    def _is_whitelisted_dunder(name: str) -> bool:
        return name in {
            "__call__",
            "__getitem__",
            "__iter__",
            "__enter__",
            "__exit__",
        }


class ForgeTyper:
    """Synthesize stub definitions from inspected protocols and schemas."""

    @classmethod
    def render_spec(
        cls, spec: ProtocolSpec, class_name: str | None = None
    ) -> str:
        name = class_name or spec.name.replace("Protocol", "Stub")
        lines = [f"class {name}:"]

        has_body = False

        for attr, attr_type in spec.attributes.items():
            lines.append(f"    {attr}: {cls._format_type(attr_type)}")
            has_body = True

        for prop, prop_type in spec.properties.items():
            lines.append("    @property")
            lines.append(
                f"    def {prop}(self) -> {cls._format_type(prop_type)}: ..."
            )
            has_body = True

        for method in spec.methods.values():
            for sig in method.signatures:
                if method.is_overloaded:
                    lines.append("    @overload")
                lines.append(
                    f"    def {method.name}{cls._format_signature(sig)}: ..."
                )
            has_body = True

        if not has_body:
            lines.append("    ...")

        return "\n".join(lines)

    @classmethod
    def draw(cls, target: type, class_name: str | None = None) -> str:
        """Draw a complete class stub from a Protocol or Mixin."""
        spec = ProtocolInspector.inspect(target)
        return cls.render_spec(spec, class_name=class_name)

    @classmethod
    def merge_and_draw(cls, targets: Sequence[type], target_name: str) -> str:
        """Compose multiple protocols/mixins into a unified stub interface."""
        merged_attrs: dict[str, type] = {}
        merged_props: dict[str, type] = {}
        merged_methods: dict[str, MethodSpec] = {}

        for target in targets:
            spec = ProtocolInspector.inspect(target)
            merged_attrs.update(spec.attributes)
            merged_props.update(spec.properties)
            merged_methods.update(spec.methods)

        composite = ProtocolSpec(
            name=target_name,
            attributes=merged_attrs,
            properties=merged_props,
            methods=merged_methods,
        )
        return cls.render_spec(composite, class_name=target_name)

    @staticmethod
    def _format_type(typ: Any) -> str:
        if typ is None or typ is type(None):
            return "None"
        if hasattr(typ, "__name__"):
            return typ.__name__
        return str(typ).replace("typing.", "")

    @classmethod
    def _format_signature(cls, sig: inspect.Signature) -> str:
        return str(sig)
