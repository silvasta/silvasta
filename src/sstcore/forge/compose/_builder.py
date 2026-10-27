"""
Define the Abstract Shape of the Composer

-
"""

__all__: list[str] = [
    "MixinBuilder",
]

from typing import Any, cast

from ...brick.field import RequiredField
from ...port.link import portlink
from ...port.shape import Builder, Mixins
from . import _mixer as mix
from ._vault import MixinRegistry


@portlink(Builder)
class MixinBuilder[BaseT: type]:
    """The Generic Engine for Class Assembly"""

    vault: RequiredField[MixinRegistry] = RequiredField(types=MixinRegistry)

    @property
    def mixins(self) -> Mixins:
        """Provide all selected internal Mixins in a stable order"""
        return self.vault.mixins

    @property
    def _topic_name(self) -> str:
        """Override this for full name Assembly"""
        return "SstBuilderMix"

    def clsname(self, name: str = "", format_name: bool = True) -> str:
        if format_name and name:
            return self._clsname(name)
        return self._default_name

    def _clsname(self, name: str) -> str:
        return f"{name}{self._topic_name}"

    @property
    def _default_name(self) -> str:
        return f"{self._topic_name}Base"

    def compose(
        self,
        *mixins: type,
        prepend: bool = True,  # LATER: some nice sort
        extras: dict | None = None,
        #
        name: str = "",
        format_name=True,
    ) -> BaseT:
        """Create a completely new class from the registry's mixins."""
        clsname: str = self.clsname(name, format_name)
        # LATER: better handling of different strategies
        bases: tuple[type, ...] = mix.Combine.combine(
            self.mixins, extras=mixins, prepend=prepend
        )
        # LATER: better handling of different strategies
        namespace: dict[str, Any] = mix.NameSpace.composition(extras=extras)

        return type(clsname, bases, namespace)  # ty:ignore

    def inject[TargeT: type](
        self,
        cls: type,
        /,
        prepend: bool = True,  # LATER: some nice sort
        extras: dict | None = None,
    ) -> TargeT:
        """Inject the registry's mixins into an existing cls class."""

        clsname: str = self.clsname(cls.__name__)
        # LATER: better handling of different strategies
        bases: tuple[type, ...] = (
            self.mixins + (cls,) if prepend else (cls,) + self.mixins
        )
        # LATER: better handling of different strategies
        namespace: dict[str, Any] = mix.NameSpace.injection(
            cls, extras=extras, spec=self
        )
        new_cls = type(clsname, bases, namespace)

        # LATER:
        # new_cls = type(
        #     self.clsname(cls.__name__),
        #     self.mixins + (cls,) if prepend else (cls,) + self.vault.mixins,
        #     mix.NameSpace.injection(cls, extras=extras, spec=self),
        # )
        if hasattr(new_cls, "model_rebuild"):  # Pydantic rebuild hook
            new_cls.model_rebuild()

        return cast(typ=TargeT, val=new_cls)
