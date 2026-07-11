from dataclasses import dataclass
from enum import Enum, auto


# 1. Define categories as Enums (strong typing + discoverability)
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
    NONE = auto()


class RichBridge(Enum):
    DELEGATE_TO_CLI = auto()
    NATIVE = auto()
    DISABLED = auto()


class Data(Enum):
    FULL = auto()
    FILTERED = auto()
    SENSITIVE = auto()
    NONE = auto()


@dataclass(frozen=True)
class ViewConfig:
    """Immutable, typed selection of view behavior."""

    identity: Identity = Identity.SHORT
    debug: Debug = Debug.REPR_LOG
    cli: Cli = Cli.PANEL
    rich_bridge: RichBridge = RichBridge.DELEGATE_TO_CLI
    data: Data = Data.FILTERED


class ViewComponentRegistry:
    """Central registry of available view mixins per category."""

    _registry: dict[type[Enum], dict[Enum, type]] = {}

    @classmethod
    def register(cls, category: type[Enum], member: Enum, mixin: type) -> None:
        """Register a mixin under a category."""
        if category not in cls._registry:
            cls._registry[category] = {}
        cls._registry[category][member] = mixin

    @classmethod
    def get(cls, category: type[Enum], member: Enum) -> type | None:
        return cls._registry.get(category, {}).get(member)

    @classmethod
    def get_all(cls, category: type[Enum]) -> dict[Enum, type]:
        return cls._registry.get(category, {}).copy()

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()


class ViewBuilder:
    """Assembles ViewMixins from a ViewConfig using the registry."""

    # Fixed ordering from most specific to base (important for MRO)
    _ORDER: list[type[Enum]] = [Identity, Debug, Cli, RichBridge, Data]

    def __init__(self, config: ViewConfig | None = None):
        self.config = config or ViewConfig()

    def with_config(self, config: ViewConfig) -> ViewBuilder:
        return ViewBuilder(config)

    def build(self) -> type[BaseView]:
        return self._assemble(self.config)

    def _assemble(self, config: ViewConfig) -> type[BaseView]:
        mixins: list[type] = []

        for category in self._ORDER:
            member = getattr(config, category.__name__.lower())
            if member == getattr(category, "NONE", None):
                continue

            mixin = ViewComponentRegistry.get(category, member)
            if mixin is None:
                raise ValueError(
                    f"No mixin registered for {category.__name__}.{member.name}"
                )
            mixins.append(mixin)

        # Always end with the base
        mixins.append(BaseView)

        # Create the composed class
        name = f"ViewMixin_{self._config_to_name(config)}"
        return type(name, tuple(mixins), {})

    @staticmethod
    def _config_to_name(config: ViewConfig) -> str:
        parts = []
        for cat in ViewBuilder._ORDER:
            val = getattr(config, cat.__name__.lower())
            if val.name != "NONE":
                parts.append(val.name.lower())
        return "_".join(parts) if parts else "minimal"


# --- Registration (done once at import time) ---


def register_default_components() -> None:
    """Register the standard set of view components."""
    # Identity
    ViewComponentRegistry.register(
        Identity, Identity.SHORT, IdentityShortMixin
    )
    ViewComponentRegistry.register(
        Identity, Identity.COLORED, IdentityColoredMixin
    )

    # Debug
    ViewComponentRegistry.register(Debug, Debug.REPR_LOG, DebugReprMixin)
    ViewComponentRegistry.register(
        Debug, Debug.REPR_LOG, DebugStructuredLogMixin
    )  # Note: can register multiple
    ViewComponentRegistry.register(
        Debug, Debug.LOG_ONLY, DebugStructuredLogMixin
    )

    # Cli
    ViewComponentRegistry.register(Cli, Cli.PANEL, CliPanelMixin)
    ViewComponentRegistry.register(
        Cli, Cli.COMPACT_PANEL, CliCompactPanelMixin
    )

    # Rich Bridge
    ViewComponentRegistry.register(
        RichBridge, RichBridge.DELEGATE_TO_CLI, RichFromCliMixin
    )

    # Data (example - would be used by other mixins internally or via __log__)
    # ViewComponentRegistry.register(Data, Data.FILTERED, FilteredDataMixin)


from pydantic import BaseModel

register_default_components()

# --- Option 1: Using ViewConfig ---
config = ViewConfig(
    identity=Identity.SHORT,
    debug=Debug.REPR_LOG,
    cli=Cli.PANEL,
    rich_bridge=RichBridge.DELEGATE_TO_CLI,
)

ViewMixin = ViewBuilder(config).build()


class Agent(ViewMixin, BaseModel):
    name: str
    tokens_used: int = 0


# --- Option 2: Fluent style ---
ViewMixin = (
    ViewBuilder()
    .with_config(
        ViewConfig(
            identity=Identity.COLORED,
            cli=Cli.COMPACT_PANEL,
        )
    )
    .build()
)

# --- Option 3: Quick default ---
DefaultView = ViewBuilder().build()


class ViewPresets:
    DEFAULT = ViewConfig()
    COMPACT = ViewConfig(
        identity=Identity.SHORT,
        cli=Cli.COMPACT_PANEL,
        rich_bridge=RichBridge.DISABLED,
    )
    DEBUG_HEAVY = ViewConfig(debug=Debug.FULL, cli=Cli.PANEL)
    PYDANTIC_FRIENDLY = ViewConfig(rich_bridge=RichBridge.NATIVE)


# Usage
ViewMixin = ViewBuilder(ViewPresets.COMPACT).build()
