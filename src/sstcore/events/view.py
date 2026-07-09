from typing import Any

from pydantic import BaseModel

from ..utils.color import colorize
from .dto import CliDTO, LogDTO, PanelDTO

# IDEA: maybe some kind of factory?
# all with __log__,__cli__ but:
# __str|repr|rich__ by toggle?


# STRATEGY: paired representation of dunders
# check as pair of same...
# - ...text: __str/rich__ but one with colors
# - ...dict: __repr/log__ but different return and purpose

# NEXT: find order!


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
