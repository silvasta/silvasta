from typing import Any

from pydantic import BaseModel

from ..color import colorize
from .dto import CliDTO, LogDTO, PanelDTO

# IDEA: maybe some kind of factory?
# all with __log__,__cli__ but:
# __str|repr|rich__ by toggle?


# STRATEGY: paired representation of dunders
# check as pair of same...
# - ...text: __str/rich__ but one with colors
# - ...dict: __repr/log__ but different return and purpose

# NEXT: find order!


class RichCliCouplerMixinSHit:
    """Bridges the custom __cli__ method to Rich Console rendering."""

    def __rich__(self) -> Any:
        if hasattr(self, "__cli__"):
            # Have your core Printer logic translate the DTO to a Rich object on the fly!
            from sstcore.utils.print import printer

            return printer._render_dto(self.__cli__())  # ty:ignore
        return str(self)


class BaseViewMixin:  # AI: how to ensure BaseModel, derive?
    """
    Generate default EventBus DTOs and string representations

    - Pydantic: use special features and Don't override amazing __rich__
    """

    def __cli__(self) -> CliDTO:
        """Create default Panel"""  # FIX: below just random
        ident = getattr(self, "name", getattr(self, "unique_id", ""))
        return PanelDTO(title=str(self), content=ident)

    def __log__(self) -> LogDTO:
        """Attach everything for json"""  # TODO: how to cut down a bit?
        if isinstance(self, BaseModel):  # TODO: create own for BaseModel?!
            data: dict[str, Any] = self.model_dump()
        else:
            data: dict[str, Any] = vars(self)
        return LogDTO(message=str(self), level="info", metrics=data)

    def __str__(self) -> str:
        # TODO: check if  needed/desired for BaseModel/dataclass
        """Show brief identifier"""
        return type(self).__name__


class ViewMixin(BaseViewMixin):  # IDEA: FmtMixin?
    """Generate default EventBus DTOs and string representations"""

    def __rich__(self) -> Any:
        """Show location of module and name of class"""
        return colorize.module_path(self)

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        attrs: str = ", ".join(
            f"{k}={v!r}"
            for k, v in vars(self).items()
            if not k.startswith("_")
        )
        return f"{type(self).__name__}({attrs})"


class LogModelMixin:
    """Provides a zero-effort __log__ serialization payload."""

    def __log__(self) -> LogDTO:
        # Gracefully handle Pydantic model vs Standard dataclasses
        if isinstance(self, BaseModel):
            metrics = self.model_dump(
                exclude={"system_prompt"}
            )  # Exclude heavy fields!
        else:
            metrics = {
                k: v for k, v in vars(self).items() if not k.startswith("_")
            }

        return LogDTO(
            message=f"{type(self).__name__} dump",
            level="INFO",
            metrics=metrics,
        )


class CliPanelMixin:
    """Provides standard Rich Panel visual representation."""

    def __cli__(self) -> PanelDTO:
        title = f"🏷️ {type(self).__name__}"
        if hasattr(self, "name"):
            title += f": {self.name}"

        metrics = {
            k: v for k, v in vars(self).items() if not k.startswith("_")
        }
        return PanelDTO(
            title=title,
            content="Resource Data Metrics",
            metrics=metrics,
            frame="blue",
        )
