"""
Define the Shape and Naming of the Builders

Implementations
- Printer: outdated status
- ViewBuilder: best example so far
- FileRegistryBuilder: in progress
- ColorBox: coming soon

"""

from typing import Any, Protocol, cast, overload


class Builder[TargetClass](Protocol):
    @property
    def mixins(self) -> tuple[type, ...]:  # NOTE: or bases
        """Provide all selected Mixins"""

    def build(
        self, name: str = "", extras: dict | None = None
    ) -> type[TargetClass]:
        # TODO: which type? how to overload types of Protocols?
        """Assemble selected Mixins to Class"""


class TypedBuilder[TargetType](Protocol):
    """Use (Mixin,Protocol) for cls:typing"""

    @property
    def types(self) -> tuple[type, ...]:
        """Provide all Protocols of selected Mixins"""

    def typing(self, type_name: str) -> TargetType:
        """Provide Type of Mixed/Merged/Melted fusioned Protocols"""


class Constructor[TargetClass](Protocol):
    """Assemble the class and directly provide an Instance"""

    def construct(self, name="", **init_kwargs: Any) -> TargetClass:
        """Inject selected Mixins to new Subclass of target cls"""


class Composer(Protocol):
    """Unsure if view is the only purpose for this or not"""

    def compose[Class: type](self, cls: Class) -> Class:  # TODO: name?
        """Inject selected Mixins to new Subclass of target cls"""

    @overload
    def __call__[Class: type](self, cls: Class, /) -> Class: ...

    @overload
    def __call__(self, /) -> type: ...

    def __call__(self, cls: type | None = None, /) -> type:
        """Inject composed mixins to Decorated target or Build class"""
        # NOTE: decorator maybe only for ViewBuilder but,
        # - most of other builder will need a view mixin


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Assembled
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Injector(Composer, Builder, Protocol):
    """TEMPORARY result for first tests"""


class Factory(Constructor, Builder, Protocol):
    """TEMPORARY result for first tests"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Testing
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class _TestTypedBuilder:
    """Use (Mixin,Protocol) for cls:typing"""

    slots: list[tuple[type, type]]  # TEST: [Mixin,Protocol]

    @property
    def mixins(self) -> tuple[type, ...]:
        return tuple(slot[0] for slot in self.slots)

    # AI: something like this?
    @property
    def types(self) -> tuple[type, ...]:
        return tuple(slot[1] for slot in self.slots)

    def typing(self, type_name: str) -> type:
        """Build the type from Protocols"""
        # AI: this or something similar possible with Python 3.14?
        return type(type_name, self.types, {})

    def build(self, name: str = "", extras: dict | None = None) -> type:
        """Sketch of an Idea"""
        target_typ: type = self.typing(f"{name}Type")
        target_cls: type = type(name, self.mixins, extras or {})
        return cast(target_typ, target_cls)
