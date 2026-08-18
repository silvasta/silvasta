"""
Compose Views at runtime and inject them into target Classes

- Work as Function, Decorator and with Args
"""

__all__: list[str] = [
    "ViewBuilder",
]

from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, cast, overload

from ...port.builder._builder import Builder, Injector, TypedBuilder
from ._mixin import MixinSentinel
from ._registry import Cli, Log, Repr, Rich, Str


@dataclass(frozen=True)
class ViewBuilder[MixClass: type]:
    """Configure ViewMixin sets and build composed classes"""

    cli: Cli = Cli.OFF
    log: Log = Log.OFF
    repr: Repr = Repr.OFF
    string: Str = Str.OFF
    rich: Rich = Rich.OFF

    def all_enums(
        self,
    ) -> tuple[Cli, Log, Repr, Str, Rich]:
        """Provide all attached member raw and unfiltered"""
        return (self.cli, self.log, self.repr, self.string, self.rich)

    def evolve(self, **changes: Any) -> Self:
        """Copy with overrides"""
        return replace(self, **changes)

    def __bool__(self) -> bool:
        return bool(self.mixins)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Builder
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    @cached_property
    def mixins(self) -> tuple[type, ...]:
        """Provide all selected Mixins in a stable order"""
        return tuple(
            mixin
            for category in self.all_enums()
            if (mixin := category.mixin) is not MixinSentinel
        )

    def mix_name(self, name="") -> str:
        """Compose name of mixed Class"""
        return f"{name}View" if name else "ViewBase"

    def build(
        self, name="", format_name=True, extras: dict | None = None
    ) -> MixClass:
        """Assemble selected Mixins to ViewBase"""
        cls_name: str = self.mix_name(name) if format_name else name or "View"
        cls: type = type(cls_name, self.mixins, extras or {})
        return cast(MixClass, cls)

    def compose(self, *mixins: type) -> Self:
        raise NotImplementedError

    def inject[Class: type](self, cls: Class) -> Class:
        """Compose selected Mixins and Inject to new Subclass of Target"""

        if not self.mixins:
            return cls

        bases: tuple[type, ...] = self.mixins + (cls,)
        namespace: dict[str, Any] = {
            "__module__": cls.__module__,
            "__qualname__": cls.__qualname__,
            "__view_spec__": self,
        }
        if hasattr(cls, "model_config"):  # Pydantic support
            namespace["model_config"] = getattr(cls, "model_config", {})

        new_cls: type = type(cls.__name__, bases, namespace)

        if hasattr(new_cls, "model_rebuild"):  # Pydantic rebuild hook
            new_cls.model_rebuild()

        return cast(Class, new_cls)

    def plus(self, *args: type):
        pass

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Execute
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    @overload
    def __call__[Class: type](self, cls: Class, /) -> Class: ...

    @overload
    def __call__(self, /) -> type: ...

    def __call__(self, cls: type | None = None, /) -> type:
        """Inject composed mixins to decorated target or build class"""

        if cls is None:
            return self.build()

        return self.inject(cls)


if TYPE_CHECKING:
    _instance_check: Builder = ViewBuilder()
    _class_check: type[Builder] = ViewBuilder
    #
    _instance_check: Injector = ViewBuilder()
    _class_check: type[Injector] = ViewBuilder
    #
    _instance_check: TypedBuilder = ViewBuilder()
    _class_check: type[TypedBuilder] = ViewBuilder
