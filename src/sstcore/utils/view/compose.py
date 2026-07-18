"""
Compose Views at runtime and inject them into target Classes

Example:
    - show main purpose of 'view' and 'ViewBuilder'

    @view(ViewBuilder(cli=Cli.LINE, str=Str.SHORT, log=Log.FULL))
    class MyCustomModel:
        "Find attached: __cli_, __str__, __log__"

"""

from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property
from typing import Any, cast

from .mixin import MixinSentinel
from .registry import Cli, Log, Repr, Rich, Str


def view[Class: type](spec: ViewBuilder) -> Callable[[Class], Class]:
    """Class Decorator: Assemble and inject ViewMixins"""

    def decorator(cls: Class) -> Class:
        return spec.compose(cls)

    return decorator


@dataclass(frozen=True)
class ViewBuilder:
    """Configure ViewMixin sets and build composed classes"""

    cli: Cli = Cli.OFF
    str: Str = Str.OFF
    rich: Rich = Rich.OFF
    repr: Repr = Repr.OFF
    log: Log = Log.OFF

    def __post_init__(self):
        if not self.mixins:
            raise ValueError("Select at least 1 Mixin for ViewBuilder!")

    def _pattern(self, name):
        return f"{name}ViewBase"

    @cached_property
    def mixins(self) -> tuple[type, ...]:
        """Provide all selected Mixins in a stable order"""
        return tuple(
            mixin
            for category in self.all_enums()
            if (mixin := category.mixin) is not MixinSentinel
        )

    def all_enums(self):
        """Provide all attached member raw and unfiltered"""
        return (self.cli, self.str, self.rich, self.repr, self.log)

    def build(self, name="", extras: dict | None = None) -> type:
        """Assemble selected Mixins to ViewBase"""

        return type(self._pattern(name), self.mixins, extras or {})

    def compose[Class: type](self, cls: Class) -> Class:
        """Inject selected Mixins to new Subclass of target cls"""

        bases: tuple[type, ...] = self.mixins + (cls,)
        namespace: dict[str, Any] = {
            "__module__": cls.__module__,
            "__qualname__": cls.__qualname__,
            "__view_spec__": self,  # TEST: Nice for debugging/introspection?
        }
        if hasattr(cls, "model_config"):  # Pydantic support
            namespace["model_config"] = getattr(cls, "model_config", {})

        new_cls: type = type(cls.__name__, bases, namespace)

        if hasattr(new_cls, "model_rebuild"):  # Pydantic rebuild hook
            new_cls.model_rebuild()

        return cast(Class, new_cls)
