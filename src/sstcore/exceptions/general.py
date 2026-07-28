from typing import Any

from ..contract.cli import Renderable
from ..utils.color import ColorBox  # WARN: ColorBox???
from .base import SstError

c = ColorBox()

__all__: list[str] = [
    "TuiSelectorError",
    "PropertyNotInitializedError",
    "NotImplementedDispatchError",
    "NotImplementedMixinError",
]


class TuiSelectorError(SstError):  # LATER: move to .ui|tui|interface?
    """Raise when App cannot continue after Selection by User"""

    def __init__(self, message=None):
        default = "It was an easy Selection... how can you Fail this?"
        super().__init__(message or default)


class PropertyNotInitializedError(SstError):
    """Raise when property is accessed before its attribute is initialized"""

    def __init__(self, property_name: str, attribute_name: str):
        self.property: str = property_name
        self.attribute: str = attribute_name

        msg = f"Missing '{attribute_name}' for property '{property_name}'"
        super().__init__(msg)

    def _modify_scroll(self, lines: list[Renderable]) -> list[Renderable]:
        """Inject property and attribute details into Error Panel"""

        property: str = c.y(self.property)
        attribute: str = c.r(self.attribute)
        line = f"{c.c('missing')}   {attribute} (required by {property})"

        _v1 = lines[:1] + [line]
        # NEXT: select
        _v2 = [lines[0], line]

        return _v2


class NotImplementedDispatchError(SstError, NotImplementedError):
    """Raise on missing TargetType for singledispatch(method)"""

    def __init__(self, first: Any, *args: Any, **kwargs):
        self.first = first
        msg = f"Missing dispatch target for {type(first).__name__}"
        super().__init__(msg, *(first, *args), **kwargs)

    def _modify_scroll(self, lines: list[Renderable]) -> list[Renderable]:
        """Inject dispatch target type and value into Error Panel"""

        missing: str = c.red("Missing match for Target")
        target_type: str = c.yellow(type(self.first).__name__)
        dispatcher: str = c.green(f"{self.first}")

        line = f"{missing} type: {target_type}, value = {dispatcher}"
        lines.insert(1, line)

        return lines


class NotImplementedMixinError(SstError, NotImplementedError):
    """Raise when Mixin queue somehow messed up"""

    def __init__(self, base, mixin, func):  # LATER: define more precise...
        self.base = base
        self.mixin = mixin
        self.func = func
        super().__init__(f"Problem for {mixin=} of {base=} in {func=}")
