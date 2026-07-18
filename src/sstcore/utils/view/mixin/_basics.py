"""
Provide shared utils for Mixins.

- str/rich or log/repr will need it

"""

from ....contract.cli import CliDTO
from ....contract.external import RichRenderable
from ....contract.log import LogDTO


class MixinSentinel:
    """Imitate a Mixin to replace None in View selection pipeline"""

    def __cli__(self) -> CliDTO:
        raise NotImplementedError

    def __log__(self) -> LogDTO:
        raise NotImplementedError

    def __rich__(self) -> RichRenderable:
        raise NotImplementedError


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### TESTING: New Ideas, work out together with Procets
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

from typing import Any  # noqa: E402

from pydantic import BaseModel  # noqa: E402

from ...parse import ParsedName  # noqa: E402


def get_display_name(obj: Any) -> str:
    """Common pattern used by str, rich, cli mixins."""
    return getattr(obj, "name", type(obj).__name__)


def get_public_data(
    obj: Any, exclude: set[str] | None = None
) -> dict[str, Any]:
    """Robust data extraction for repr, log, cli panels."""
    exclude = exclude or {"system_prompt", "message_history"}
    if isinstance(obj, BaseModel):
        return obj.model_dump(exclude=exclude)
    return {
        k: v
        for k, v in vars(obj).items()
        if not k.startswith("_") and k not in exclude
    }


class ViewMixinBase:
    """Optional base for mixins that want the helpers as methods."""

    def _get_name(self) -> str:
        return get_display_name(self)

    def _get_data(self, exclude: set[str] | None = None) -> dict[str, Any]:
        return get_public_data(self, exclude)


class ViewNameBase:
    """Base class for view mixins that allows pattern injection."""

    # Classes using this mixin can override this template!
    _NAME_TEMPLATE = ParsedName("[bold cyan]{cls_name}[/] (id={id})")

    def _get_template_kwargs(self) -> dict:
        """Extracts data for the template. Classes can override this."""
        return {
            "cls_name": type(self).__name__,
            "id": getattr(self, "id", "N/A"),
        }
