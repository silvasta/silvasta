# TODO: explain

from typing import Any

from rich.panel import Panel

from ..utils.color import ColorBox

c = ColorBox()

# NEXT: exceptions - must be complete until bump
# TASK: here is precise work without any failure needed
# - ensure root is 100% perfect
# - check all others at least twice


class SstError(Exception):
    """Root of all Custom Exceptions"""

    def __init__(self, *args, **kwargs):
        self.kwargs: dict = kwargs
        # Exception handles *args and stores them in self.args
        super().__init__(*args)  # Do NOT pass kwargs up to Exception

    def __repr__(self):
        attrs: str = ", ".join(
            f"{k}={v!r}"
            for k, v in vars(self).items()
            if not k.startswith("_")
        )
        return f"{type(self).__name__}({attrs})"

    def __rich__(self):
        """Provide Panel Template"""

        rows: list[str] = [
            f"{c.r(self._name)}",
            f"{c.c('args')}    {self.args or self._default}",
            f"{c.c('kwargs')}  {self.kwargs or self._default}",
        ]

        self._modify_if_needed(rows)

        return Panel(
            "\n".join(rows),
            title=c(self._title, color="bold white"),
            border_style="red",
            title_align="right",
        )

    def _modify_if_needed(self, rows: list[str]):
        """Use this for modification in Subclasses"""

    @property
    def _title(self):
        return f"{type(self).__name__[:-5]}{c.red('Error')}"

    @property
    def _name(self):
        return type(self).__name__

    @property
    def _default(self):
        return "nothing attached"


# IMPORTANT: MixinError! maybe BusError?

# TASK: PathGuard Error??


class RegistrySyncError(SstError):
    """Raise when FileRegistry State mismatches physical local disk"""

    # LATER: setup for different FileTrackerRegistry


class NotImplementedDispatchError(SstError, NotImplementedError):
    """Raise on missing TargetType for singledispatchmethod"""

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
    """Raised when Mixin queue somthing mixed up"""

    def __init__(self, base, mixin, func):
        self.base = base
        self.mixin = mixin
        self.func = func
        super().__init__(f"Problem for {mixin=} of {base=} in {func=}")


class TuiSelectorError(SstError):
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
