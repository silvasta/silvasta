from typing import Any

from rich.panel import Panel

from ..utils.paint import ColorBox

c = ColorBox()


class SstError(Exception):
    """Root of all Custom Exceptions"""

    # FIX: check gemini chat .args and ._kwargs???
    # - maybe property below broken

    def __str__(self, *args, **kwargs):
        # TODO: attach something?
        return super().__str__(*args, **kwargs)

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
            f"{c.b('args')}    {self._args or 'not loaded'}",
            f"{c.b('kwargs')}  {self._kwargs or 'not loaed'}",
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
    def _args(self) -> tuple | str:
        return getattr(self, "args", self._default)

    @property
    def _default(self):
        return "nothing attached"

    @property
    def _kwargs(self) -> dict | None:
        return getattr(self, "kwargs", self._default)


class RegistrySyncError(FileNotFoundError, SstError):
    """Raise when FileRegistry State mismatches physical local disk"""


class NotImplementedDispatchError(NotImplementedError, SstError):
    """Raise on missing TargetType for singledispatchmethod"""

    def __init__(self, first: Any, *args: Any, **kwargs):
        self.first = first
        self.args: tuple[Any] = args
        self.kwargs: dict = kwargs or {}
        super().__init__(type(first).__name__)

    def __rich__(self) -> Panel:  # LATER: merge with template
        """Provide the first nice plots! ...done"""

        error: str = type(self).__name__
        target = "Missing match for Target"
        target_type = type(self.first).__name__

        rows: list[str] = [
            f"{c.r(error)}",
            f"{c.r(target)} type: {c.y(target_type)}, value = {c.g(f'{self.first}')}",
            f"{c.b('args')}    {self.args or 'not loaded'}",
            f"{c.b('kwargs')}  {self.kwargs or 'not loaed'}",
        ]
        return Panel(
            "\n".join(rows),
            title=c("NotImplementedDispatchError", color="bold white"),
            border_style="red",
            title_align="right",
        )


class NotImplementedMixinError(NotImplementedError, SstError):
    """Raised when Mixin queue somthing mixed up"""

    def __init__(self, base, mixin, func):
        self.base = base
        self.mixin = mixin
        self.func = func
        super().__init__(f"Problem for {mixin=} of {base=} in {func=}")


class TuiSelectorError(RuntimeError, SstError):
    def __init__(self, message=None):
        if message is None:
            message = "It was an easy Selection... how can you Fail this?"
        super().__init__(message)
