"""
Define the Shape of Exceptions

- SstError: The Root

"""

__all__: list[str] = [
    "SstError",
    "RegistrySyncError",
    "NotImplementedDispatchError",
    "NotImplementedMixinError",
    "TuiSelectorError",
    "PropertyNotInitializedError",
]

from typing import Any

from ..contract.cli import PanelDTO
from ..contract.log import LogDTO
from ..utils.color import ColorBox  # WARN: ColorBox???

c = ColorBox()

# IDEA: PathGuard Error??
# NEXT: exceptions - must be complete until bump
# TASK: here is precise work without any failure needed
# - ensure root is 100% perfect
# - check all others at least twice


class SstError(Exception):
    """Define the View and Behaviour of Custom Errors"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Store Kwargs as builtins.Exception only handles Args"""
        self.kwargs: dict = kwargs
        super().__init__(*args)

    def _modify_if_needed(self, rows: list[str]) -> None:
        """Use this for modification in Subclasses"""

    @property
    def _default(self) -> str:
        return "nothing attached"

    def __cli__(self) -> PanelDTO:
        """Provide Data Transfer Object for CLI Rendering"""

        rows: list[str] = [
            f"{c.r(self.name)}",
            f"{c.c('args')}    {self.args or self._default}",
            f"{c.c('kwargs')}  {self.kwargs or self._default}",
        ]

        self._modify_if_needed(rows)

        return PanelDTO(
            text="\n".join(rows),
            title=self.__rich__(),
            frame="red",
            title_align="right",
        )

    @property
    def name(self) -> str:
        """Provide Name like __str__ because Exceptions use it for message"""
        return type(self).__name__

    def __rich__(self) -> str:
        """Provide colorized Name"""
        return f"{self.name[:-5]}{c.red('Error')}"

    def __repr__(self):
        """Provide Structured Data flattened to string"""
        attributes: list[str] = [f"args={self.args!r}"]
        attributes.extend(
            f"{k}={v!r}"
            for k, v in vars(self).items()
            if not k.startswith("_")
        )
        return f"{self.name}({', '.join(attributes)})"

    def __log__(self) -> LogDTO:
        """Provide Structured Data for Log"""
        return LogDTO(
            message=str(self) or self.name,
            level="ERROR",
            metrics={"args": self.args, "kwargs": self.kwargs},
            extra={"error_type": self.name},
        )


class RegistrySyncError(SstError):  # LATER: setup for FileTrackerRegistry
    """Raise when FileRegistry State mismatches physical local disk"""


class NotImplementedDispatchError(SstError, NotImplementedError):
    """Raise on missing TargetType for singledispatch(method)"""

    def __init__(self, first: Any, *args: Any, **kwargs):
        self.first = first
        msg = f"Missing dispatch target for {type(first).__name__}"
        super().__init__(msg, *(first, *args), **kwargs)

    def _modify_if_needed(self, rows: list[str]):
        """Inject dispatch target type and value into Error Panel"""

        missing: str = c.red("Missing match for Target")
        target_type: str = c.yellow(type(self.first).__name__)
        dispatcher: str = c.green(f"{self.first}")

        line = f"{missing} type: {target_type}, value = {dispatcher}"

        rows.insert(1, line)


class NotImplementedMixinError(SstError, NotImplementedError):
    """Raise when Mixin queue somehow messed up"""

    def __init__(self, base, mixin, func):
        self.base = base
        self.mixin = mixin
        self.func = func
        super().__init__(f"Problem for {mixin=} of {base=} in {func=}")


class TuiSelectorError(SstError):
    """Raise when App cannot continue after Selection by User"""

    def __init__(self, message=None):
        if message is None:
            message = "It was an easy Selection... how can you Fail this?"
        super().__init__(message)


class PropertyNotInitializedError(SstError):
    """Raise when property is accessed before its attribute is initialized"""

    def __init__(self, property_name: str, attribute_name: str):
        self.property: str = property_name
        self.attribute: str = attribute_name

        msg = f"Missing '{attribute_name}' for property '{property_name}'"
        super().__init__(msg)

    def _modify_if_needed(self, rows: list[str]):
        """Inject property and attribute details into Error Panel"""

        property: str = c.y(self.property)
        attribute: str = c.r(self.attribute)
        line = f"{c.c('missing')}   {attribute} (required by {property})"

        rows.insert(1, line)
        del rows[2:]
