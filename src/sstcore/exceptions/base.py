from typing import Any

from rich import inspect
from rich.control import strip_control_codes
from rich.panel import Panel
from rich.text import Text


def test_this_somewhennnn(text: str) -> str:
    """Fix broken or undesired color pattern"""
    inspect(text)
    return strip_control_codes(text)


class SstError(Exception):
    """Root of all custom Exceptions"""


class RegistrySyncError(FileNotFoundError, SstError):
    """Raise when FileRegistry State mismatches physical local disk"""


class NotImplementedDispatchError(NotImplementedError, SstError):
    """Raise on missing TargetType for singledispatchmethod"""

    def __init__(self, first: Any, *args: Any, **kwargs):
        self.first = first
        self.args: tuple[Any] = args
        self.kwargs: dict = kwargs or {}
        super().__init__(type(first).__name__)

    def __rich__(self) -> Panel:
        """Rich protocol hook. Triggered by console.print(error)"""
        text = Text()
        text.append("Missing TargetType: ", style="bold red")
        text.append(f"{type(self.first).__name__}\n", style="bold yellow")
        text.append(f"Target Value: {self.first}\n\n", style="dim")
        text.append(f"Args: {self.args}\n", style="cyan")
        text.append(f"Kwargs: {self.kwargs}", style="magenta")
        return Panel(
            text, title="NotImplementedDispatchError", border_style="red"
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
