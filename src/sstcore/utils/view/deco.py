from collections.abc import Callable
from enum import Enum, auto

from pydantic import BaseModel


# views/identity.py
class IdentityShortMixin:
    """Minimal name - good default for __str__"""

    def __str__(self) -> str:
        name = getattr(self, "name", None)
        return (
            f"{type(self).__name__}({name})" if name else type(self).__name__
        )


class IdentityColoredMixin:
    """Colored version for Rich (pair with above)"""

    def __rich__(self) -> str:
        from sstcore.utils.color import colorize

        return colorize.module_path(self)  # or a nicer version


# views/debug.py
class DebugReprMixin:
    """Standard detailed repr"""

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in vars(self).items()
            if not k.startswith("_")
        )
        return f"{type(self).__name__}({attrs})"


class DebugStructuredLogMixin:
    """Good for __log__ - can be used independently"""

    def __log__(self) -> LogDTO:
        data = self.model_dump() if hasattr(self, "model_dump") else vars(self)
        # Consider filtering here or in a Data mixin
        return LogDTO(message=str(self), level="INFO", metrics=data)


# views/cli.py
class CliPanelMixin:
    """Default reasonable panel"""

    def __cli__(self) -> PanelDTO:
        title = getattr(self, "name", type(self).__name__)
        data = self.model_dump() if hasattr(self, "model_dump") else vars(self)
        return PanelDTO(
            title=title, content="Data", metrics=data, frame="cyan"
        )


class CliCompactPanelMixin:
    """Smaller panel - useful for lists"""

    def __cli__(self) -> PanelDTO:
        title = getattr(self, "name", type(self).__name__)
        return PanelDTO(title=title, content="", metrics={}, frame="dim")


# views/rich_bridge.py
class RichFromCliMixin:
    """Implements __rich__ by delegating to __cli__.
    Only use this when you want to bypass Pydantic's __rich__.
    """

    def __rich__(self):
        from sstcore.utils.print import printer

        if hasattr(self, "__cli__"):
            return printer._render_dto(self.__cli__())
        return str(self)


class Identity(Enum):
    SHORT = auto()
    COLORED = auto()
    QUALIFIED = auto()
    NONE = auto()


class Debug(Enum):
    REPR_LOG = auto()
    REPR_ONLY = auto()
    LOG_ONLY = auto()
    FULL = auto()
    NONE = auto()


class Cli(Enum):
    PANEL = auto()
    COMPACT_PANEL = auto()
    LINE = auto()
    TABLE = auto()
    MARKDOWN = auto()
    NONE = auto()


class RichBridge(Enum):
    """Controls how __rich__ behaves"""

    DELEGATE_TO_CLI = auto()  # __rich__ calls __cli__
    NATIVE = auto()  # Keep original __rich__ (important for Pydantic)
    DISABLED = auto()


class DataProfile(Enum):
    """Controls how much data is exposed"""

    FULL = auto()
    FILTERED = auto()
    SENSITIVE_SAFE = auto()
    NONE = auto()


from . import cli, debug, identity, rich_bridge  # ty:ignore

VIEW_REGISTRY: dict[Enum, type] = {
    # Identity
    Identity.SHORT: identity.IdentityShortMixin,
    Identity.COLORED: identity.IdentityColoredMixin,
    Identity.QUALIFIED: identity.IdentityQualifiedMixin,
    # Debug
    Debug.REPR_LOG: debug.DebugReprLogMixin,
    Debug.REPR_ONLY: debug.DebugReprMixin,
    Debug.LOG_ONLY: debug.DebugStructuredLogMixin,
    # CLI
    Cli.PANEL: cli.CliPanelMixin,
    Cli.COMPACT_PANEL: cli.CliCompactPanelMixin,
    Cli.LINE: cli.CliLineMixin,
    Cli.TABLE: cli.CliTableMixin,
    # Rich Bridge
    RichBridge.DELEGATE_TO_CLI: rich_bridge.RichFromCliMixin,
    # Data
    DataProfile.FILTERED: debug.FilteredDataMixin,
    DataProfile.FULL: debug.FullDataMixin,
}


def _resolve_mixins(
    identity: Identity,
    debug: Debug,
    cli: Cli,
    rich_bridge: RichBridge,
    data: DataProfile,
) -> list[type]:
    """Resolve selected enums into mixin classes."""
    selected: list[type] = []

    for category in (identity, debug, cli, rich_bridge, data):
        if category in VIEW_REGISTRY:
            selected.append(VIEW_REGISTRY[category])

    return selected


def view[T: type](
    *,
    identity: Identity = Identity.SHORT,
    debug: Debug = Debug.REPR_LOG,
    cli: Cli = Cli.PANEL,
    rich_bridge: RichBridge = RichBridge.DELEGATE_TO_CLI,
    data: DataProfile = DataProfile.FILTERED,
) -> Callable[[T], T]:
    """
    Class decorator that assembles and injects a ViewMixin.

    Example:
        @view(identity=Identity.COLORED, cli=Cli.PANEL)
        class Agent(BaseModel):
            ...
    """

    def decorator(cls: T) -> T:
        mixins = _resolve_mixins(identity, debug, cli, rich_bridge, data)

        if not mixins:
            return cls

        # Create the composed view base
        ViewBase = type(
            f"{cls.__name__}View",
            tuple(mixins),
            {"__module__": cls.__module__},
        )

        # Prepend the view base to the inheritance chain.
        # This is important for MRO.
        original_bases = cls.__bases__

        # Create new class with injected view behavior
        new_cls = type(
            cls.__name__,
            (ViewBase,) + original_bases,
            dict(cls.__dict__),
        )

        # Preserve important metadata
        new_cls.__module__ = cls.__module__
        new_cls.__qualname__ = cls.__qualname__

        # Special handling for Pydantic models (v2)
        if hasattr(cls, "model_config"):
            # Re-apply model configuration if needed
            new_cls.model_config = cls.model_config

        return new_cls  # type: ignore[return-value]

    return decorator


@view(identity=Identity.SHORT, cli=Cli.PANEL)
class Agent(BaseModel):
    name: str
    tokens_used: int = 0


@view(
    identity=Identity.COLORED,
    debug=Debug.REPR_LOG,
    cli=Cli.COMPACT_PANEL,
    rich_bridge=RichBridge.NATIVE,  # Important for some Pydantic cases
)
class ComplexResource(BaseModel):
    id: str
    config: dict


# views/__init__.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cli import CliPanelMixin
    from .debug import DebugReprLogMixin
    from .identity import IdentityShortMixin
    from .rich_bridge import RichFromCliMixin

    class ViewMixin(
        IdentityShortMixin,
        DebugReprLogMixin,
        CliPanelMixin,
        RichFromCliMixin,
    ): ...
else:
    ViewMixin = object  # dummy at runtime


from dataclasses import dataclass


@dataclass
class ViewConfig:
    identity: Identity = Identity.SHORT
    debug: Debug = Debug.REPR_LOG
    cli: Cli = Cli.PANEL
    rich_bridge: RichBridge = RichBridge.DELEGATE_TO_CLI
    data: DataProfile = DataProfile.FILTERED


@view(config=ViewConfig(cli=Cli.TABLE, debug=Debug.FULL))
class Something(BaseModel): ...
