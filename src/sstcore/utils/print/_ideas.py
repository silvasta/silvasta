from dataclasses import dataclass
from typing import Any

from rich import inspect
from rich.control import strip_control_codes
from rich.panel import Panel


def test_this_somewhennnn(text: str) -> str:
    """Fix broken or undesired color pattern"""
    inspect(text)  # LATER: inspect rich.inspect
    return strip_control_codes(text)


@dataclass
class PanelStyle:  # COLLECT: panel style DTO
    title: str | None = None
    text_style: str | None = None
    frame: str | None = "cyan"
    padding: tuple = (1, 1)


class BasePrinter:
    PANEL_KWARGS: set[str] = {  # LATER: panel split kwarg trick
        "box",
        "safe_box",
        "expand",
        "padding",
        "subtitle",
        "border_style",
    }

    def __call__(self, *args, **kwargs):
        pass

    def panel(self, target: Any, **kwargs) -> None:
        #
        # ... pop custom args ...

        # Split kwargs: one dict for Panel, one for the Printer
        panel_kwargs: dict[str, Any] = {
            k: v for k, v in kwargs.items() if k in self.PANEL_KWARGS
        }
        print_kwargs: dict[str, Any] = {
            k: v for k, v in kwargs.items() if k not in self.PANEL_KWARGS
        }
        panel_obj = Panel(target, **panel_kwargs)
        self(panel_obj, **print_kwargs)
