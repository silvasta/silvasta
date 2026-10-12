"""
The TypedBuilder

- so far only a dream...

"""

__all__: list[str] = [
    #
]

from typing import Protocol, cast


class _TypedBuilder[TargetType](Protocol):
    """Use (Mixin,Protocol) for cls:typing"""

    @property
    def types(self) -> tuple[type, ...]:
        """Provide all Protocols of selected Mixins"""

    def typing(self, type_name: str) -> TargetType:
        """Provide Type of Mixed/Merged/Melted fusioned Protocols"""


class _TestTypedBuilder:
    """Use (Mixin,Protocol) for cls:typing"""

    slots: list[tuple[type, type]]  # TEST: [Mixin,Protocol]

    @property
    def mixins(self) -> tuple[type, ...]:
        return tuple(slot[0] for slot in self.slots)

    @property
    def types(self) -> tuple[type, ...]:
        return tuple(slot[1] for slot in self.slots)

    def typing(self, type_name: str) -> type:
        """Build the type from Protocols"""
        return type(type_name, self.types, {})

    def build(self, name: str = "", extras: dict | None = None) -> type:
        """Sketch of an Idea"""
        target_typ: type = self.typing(f"{name}Type")
        target_cls: type = type(name, self.mixins, extras or {})
        return cast(target_typ, target_cls)
