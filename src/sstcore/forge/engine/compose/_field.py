"""
Prepare, Hold and Distribute the Mixins (and Protocols) with Fields

-
"""

from typing import Any

__all__: list[str] = [
    # "MixinRegistry",
    # "DuoRegistry",
]


from ....brick.field import LazyField, ReadField, ValidField
from ....port.register import Registry
from ..typed._detect import is_protocol


class SlotPair:
    """Normalized stable container. Cannot be instantiated empty."""

    __slots__ = ("mixin", "proto")

    def __init__(self, mixin: type | None = None, proto: type | None = None):
        if mixin is None and proto is None:
            raise ValueError("SlotPair Empty!")

        self.mixin: type | None = mixin
        self.proto: type | None = proto

    @property
    def is_complete(self) -> bool:
        return self.mixin is not None and self.proto is not None


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type SlotInput = tuple[type, type] | type | SlotPair

type SlotOutput = SlotPair


class RegistryField(ValidField[SlotInput], ReadField):
    """Guarante that the underlying state is always a valid SlotPair"""

    def validate(self, unit: object, value: SlotInput) -> SlotPair:
        if isinstance(value, SlotPair):
            return value
        if isinstance(value, tuple):
            if len(value) == 2:
                return SlotPair(mixin=value[0], proto=value[1])
        self.on_error.Validation(unit=unit, value=value)
        if isinstance(value, type):
            if is_protocol(value):
                return SlotPair(mixin=None, proto=value)
            else:
                return SlotPair(mixin=value, proto=None)
        raise self.on_error.Validation(unit=unit, value=value)

    def read(self, unit: object) -> SlotOutput:
        return super().read(unit)


class RegistryDescriptor(LazyField, ValidField):
    """Mounts the Vault and proxies writes to the Vault's native methods."""

    def __init__(self, registry_type: type[Registry], *args, **kwargs):
        self.registry_type = registry_type
        super().__init__(*args, **kwargs)

    def write(self, unit: object, value: Any) -> None:
        """Intercept direct assignment and route to vault.add()"""
        vault: Registry = self.read(unit)

        if isinstance(value, (list, tuple, dict)):
            vault.clear()
            vault.add(*value)
        else:
            vault.add(value)
