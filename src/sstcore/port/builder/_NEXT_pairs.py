from typing import Any, NamedTuple, Protocol, cast, runtime_checkable

from typing_extensions import TypeForm

_TEST_LATER = TypeForm

# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:


class Composition[P](NamedTuple):
    """Result of a dynamic composition."""

    cls: type[Any]  # the concrete runtime class
    proto: type[P]  # the combined Protocol (best-effort)


def compose_with_proto(
    base: type[Any],
    pairs: list[tuple[type[Any], type[Any]]],  # (Mixin, Protocol)
) -> Composition:
    """Dynamically compose selected (mixin, protocol) pairs"""
    if not pairs:
        raise ValueError("pairs must not be empty")

    mixins = [m for m, _ in pairs]
    protocols = [p for _, p in pairs]

    @runtime_checkable
    class CombinedProtocol(*protocols, Protocol): ...

    name = f"Composed_{base.__name__}_" + "_".join(m.__name__ for m in mixins)
    concrete = type(name, (*mixins, base), {})

    concrete.__protocol__ = CombinedProtocol

    return Composition(concrete, CombinedProtocol)


def compose_with_cast(
    base: type[Any],
    pairs: list[tuple[type[Any], type[Any]]],  # (Mixin, Protocol)
):
    """Dynamically compose selected (mixin, protocol) pairs"""
    if not pairs:
        raise ValueError("pairs must not be empty")

    mixins = [m for m, _ in pairs]
    protocols = [p for _, p in pairs]

    @runtime_checkable
    class CombinedProtocol(*protocols, Protocol): ...

    name = f"Composed_{base.__name__}_" + "_".join(m.__name__ for m in mixins)
    concrete = type(name, (*mixins, base), {})

    casted = cast(CombinedProtocol, concrete)

    return casted


class Base: ...


class MixinA: ...


class ProtoA(Protocol): ...


class MixinB: ...


class ProtoB(Protocol): ...


@runtime_checkable
class ProtoCombi(ProtoA, ProtoB, Protocol): ...


Selected = [
    (MixinA, ProtoA),
    (MixinB, ProtoB),
]

casted_cls = compose_with_cast(Base, Selected)
if isinstance(casted_cls(), ProtoCombi):
    raise RuntimeError

composed = compose_with_proto(Base, Selected)

new_class = composed.cls
new_proto = composed.proto

if isinstance(new_class(), ProtoCombi):
    raise RuntimeError
else:
    pass

if isinstance(new_class(), composed.proto):
    raise RuntimeError
else:
    pass

instance = new_class()
typed_instance = cast(composed.proto, new_class())
typed_instance2: ProtoCombi = new_class()

# 3. If you really want the dynamic one (weaker)
instance_dyn = cast(new_proto, new_class())

# 1. Use the static combined protocol you already defined
instance_good: ProtoCombi = new_class()

# 2. Cast through the static protocol
instance_cast = cast(ProtoCombi, new_class())


# Runtime check still works thanks to @runtime_checkable
assert isinstance(instance, new_proto)

cast(new_proto, instance)

x = instance
