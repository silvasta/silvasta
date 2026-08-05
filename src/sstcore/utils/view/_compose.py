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
class ViewBuilder:
    """Configure ViewMixin sets and build composed classes"""

    # TASK: check: allow unregistered Mixins
    # - replace 1-5 of the categories by a free mixin
    # - use isinstance(...) to confirm it is valid
    # sometimes just 1 is missing and for that some bypass should be considered
    # - build and inject by regular class Foo(_View) anyway possible
    # - balance extra comfort and extra risk + complexity

    cli: Cli = Cli.OFF
    str: Str = Str.OFF
    rich: Rich = Rich.OFF
    repr: Repr = Repr.OFF
    log: Log = Log.OFF

    @cached_property
    def mixins(self) -> tuple[type, ...]:
        """Provide all selected Mixins in a stable order"""
        return tuple(
            mixin
            for category in self.all_enums()
            if (mixin := category.mixin) is not MixinSentinel
        )

    def __bool__(self) -> bool:
        return bool(self.mixins)

    def all_enums(self) -> tuple:
        """Provide all attached member raw and unfiltered"""
        return (self.cli, self.str, self.rich, self.repr, self.log)

    def evolve(self, **changes: Any) -> Self:
        """Copy with overrides"""
        return replace(self, **changes)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Assemble
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def build(self, name="", extras: dict | None = None) -> type:
        """Assemble selected Mixins to ViewBase"""

        return type(f"{name}ViewBase", self.mixins, extras or {})

    def compose[Class: type](self, cls: Class) -> Class:
        # IMPORTANT: check naming, maybe this to inject?
        """Inject selected Mixins to new Subclass of target cls"""

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

        return self.compose(cls)


if TYPE_CHECKING:
    _instance_check: Builder = ViewBuilder()
    _class_check: type[Builder] = ViewBuilder
    #
    _instance_check: TypedBuilder = ViewBuilder()
    _class_check: type[TypedBuilder] = ViewBuilder
    #
    _instance_check: Injector = ViewBuilder()
    _class_check: type[Injector] = ViewBuilder
