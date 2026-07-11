from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from ..color import colorize
from .dto import CliDTO, LineDTO, LogDTO, PanelDTO

# ------------------------------------------------------------------ #
# Category Mixins
# ------------------------------------------------------------------ #


class SimpleNameMixin:
    """__str__ → just the class name (most minimal)."""

    def __str__(self) -> str:
        return type(self).__name__


class StyledNameMixin:
    """__str__ → ClassName: identifier (recommended default)."""

    def __str__(self) -> str:
        name = type(self).__name__
        if hasattr(self, "name") and self.name:
            name += f": {self.name}"
        return name


class ModulePathRichMixin:
    """__rich__ → colored module path (good for library classes)."""

    def __rich__(self) -> Any:
        return colorize.module_path(self)


class FilteredReprMixin:
    """__repr__ → only public attributes (best default for debugging)."""

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in vars(self).items()
            if not k.startswith("_")
        )
        return f"{type(self).__name__}({attrs})"


class FullReprMixin:
    """__repr__ → everything (including private)."""

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({attrs})"


class LogModelMixin:
    """__log__ that respects Pydantic and can exclude heavy fields."""

    def __log__(self) -> LogDTO:
        if isinstance(self, BaseModel):
            metrics = self.model_dump(
                exclude={"system_prompt", "message_history"}
            )
        else:
            metrics = {
                k: v for k, v in vars(self).items() if not k.startswith("_")
            }
        return LogDTO(
            message=f"{type(self).__name__} loaded",
            level="INFO",
            metrics=metrics,
        )


class CliPanelMixin:
    """Default nice panel (recommended)."""

    def __cli__(self) -> PanelDTO:
        title = f"{type(self).__name__}"
        if hasattr(self, "name") and self.name:
            title += f": {self.name}"

        metrics = (
            self.model_dump(exclude={"system_prompt", "message_history"})
            if isinstance(self, BaseModel)
            else {k: v for k, v in vars(self).items() if not k.startswith("_")}
        )
        return PanelDTO(
            title=title,
            content="Resource Data",
            metrics=metrics,
            frame="blue",
        )


class CliLineMixin:
    """Simple one-line output."""

    def __cli__(self) -> LineDTO:
        return LineDTO(
            message=str(self),
            style="cyan",
        )


# ------------------------------------------------------------------ #
# Factory (the heart of the system)
# ------------------------------------------------------------------ #


def create_view_mixin(
    name: str = "styled",  # "simple" | "styled"
    rich: str = "cli_coupler",  # "module" | "cli_coupler"
    repr_style: str = "filtered",  # "filtered" | "full"
    log: str = "model",  # "model"
    cli: str = "panel",  # "panel" | "line"
) -> type:
    """Dynamically compose a ViewMixin from chosen behaviours."""
    chain: list[type] = []

    # Name category
    if name == "styled":
        chain.append(StyledNameMixin)
    else:
        chain.append(SimpleNameMixin)

    # Rich category
    if rich == "module":
        chain.append(ModulePathRichMixin)
    else:
        pass
        # chain.append(RichCliCouplerMixin)

    # Repr category
    if repr_style == "full":
        chain.append(FullReprMixin)
    else:
        chain.append(FilteredReprMixin)

    # Log & CLI categories (order matters – more specific first)
    if log == "model":
        chain.append(LogModelMixin)
    if cli == "line":
        chain.append(CliLineMixin)
    else:
        chain.append(CliPanelMixin)

    # Base last
    chain.append(
        BaseViewMixin
    )  # provides fallback __cli__ / __log__ / __str__

    return type("ViewMixin", tuple(chain), {})


# ------------------------------------------------------------------ #
# Public default + TYPE_CHECKING stub
# ------------------------------------------------------------------ #


class BaseViewMixin:
    """Fallbacks – rarely reached if you pick good mixins above."""

    def __cli__(self) -> CliDTO:
        ident = getattr(self, "name", getattr(self, "unique_id", str(self)))
        return PanelDTO(title=str(self), content=ident)

    def __log__(self) -> LogDTO:
        return LogDTO(message=str(self), level="INFO", metrics={})


_DefaultViewMixin = create_view_mixin()

if TYPE_CHECKING:
    # Full static version for perfect IDE support
    class ViewMixin(
        StyledNameMixin,
        FilteredReprMixin,
        LogModelMixin,
        CliPanelMixin,
        BaseViewMixin,
    ):
        pass
else:
    ViewMixin = _DefaultViewMixin
