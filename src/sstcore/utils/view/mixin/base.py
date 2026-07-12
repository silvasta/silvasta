"""
Provide shared utils for Mixins

- str/rich or log/repr will need it

"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Ideas
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

from typing import Any

from pydantic import BaseModel


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
