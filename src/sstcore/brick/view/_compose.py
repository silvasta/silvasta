"""
Compose Views at runtime and inject them into target Classes

- Work as Function, Decorator and with Args
"""

__all__: list[str] = [
    "ViewComposer",
]

from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, cast, overload

from ...brick.forge.mix import combine_mixins
from ...port.register import MixinRegister
from ...port.shape import Composer
from ._mixin import MixinSentinel
from ._registry import Cli, Log, Repr, Rich, Str

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
# NEXT:


@dataclass(frozen=True)
class ViewComposer[ViewBase: type]:
    """Configure ViewMixin sets and build composed classes"""

    cli: Cli = Cli.OFF
    log: Log = Log.OFF
    repr: Repr = Repr.OFF
    string: Str = Str.OFF
    rich: Rich = Rich.OFF

    def evolve(self, **changes: Any) -> Self:
        """Copy with overrides"""
        return replace(self, **changes)

    def all_enums(
        self,
    ) -> tuple[Cli, Log, Repr, Str, Rich]:
        """Provide all attached ViewRegistry member"""
        return (self.cli, self.log, self.repr, self.string, self.rich)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Composer(Protocol)
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def mix_name(self, name="") -> str:
        return f"{name}View" if name else "ViewBase"

    @cached_property
    def mixins(self) -> tuple[type, ...]:
        """Provide all selected internal Mixins in a stable order"""
        return tuple(
            mixin
            for category in self.all_enums()
            if (mixin := category.mixin) is not MixinSentinel
        )

    # REMOVE: combine build/inject to mix
    def build(
        self,
        name="",
        format_name=True,
        extras: dict | None = None,
        *,
        mixins: tuple[type, ...] = (),
        prepend: bool = True,
    ) -> ViewBase:
        """Assemble selected Mixins to ViewBase"""
        cls_name: str = self.mix_name(name) if format_name else name or "View"
        bases: tuple[type, ...] = combine_mixins(
            self.mixins, mixins, prepend=prepend
        )
        new_cls: type = type(cls_name, bases, extras or {})

        return cast(typ=ViewBase, val=new_cls)

    # REMOVE: combine build/inject to mix
    def inject[Target: type](
        self,
        cls: Target,
        /,
        *mixins: type,
        prepend: bool = True,
    ) -> Target:
        """Compose selected Mixins and Inject to new Subclass of Target"""

        # AI: this method looks for example way to heavy for the registry,
        # - maybe this method with others in a BuilderBox inside brick
        # - ViewComposer takes the functions from there and the mixins from registry
        if not (bases := combine_mixins(self.mixins, mixins, prepend=prepend)):
            return cls

        namespace: dict[str, Any] = {
            "__module__": cls.__module__,
            "__qualname__": cls.__qualname__,
            "__view_spec__": self,
        }
        if hasattr(cls, "model_config"):  # Pydantic support
            namespace["model_config"] = getattr(cls, "model_config", {})

        new_cls: type = type(cls.__name__, (*bases, cls), namespace)

        if hasattr(new_cls, "model_rebuild"):  # Pydantic rebuild hook
            new_cls.model_rebuild()

        return cast(typ=Target, val=new_cls)

    @overload
    def mix[MixInjected](
        self,
        cls: type,
    ) -> MixInjected: ...
    @overload
    def mix(
        self,
        cls: None,
    ) -> ViewBase: ...

    def mix[
        MixInjected: type
    ](  # # TODO: maybe insert here mixed proto? for cast?
        self,
        cls: type | None = None,
        *,
        mixins: tuple[type, ...] = (),
        data: MixinRegister[MixInjected],
    ) -> ViewBase | MixInjected:
        """Build new Class from Mixins or Inject to Target for new Subclass"""

        # AI: it makes no sense to insert mixins and data together,
        # at least 1 should be already attached before,
        # anyway I hope the idea is clear how to handle the registry:
        # - use it like a mobile jukebox, handing around, butten pressed for some action
        if mixins:
            data.add(mixins)

        if cls is None:
            return data.build()
        else:
            return data.inject()


if TYPE_CHECKING:
    _instance_check: Composer = ViewComposer()
    _class_check: type[Composer] = ViewComposer
