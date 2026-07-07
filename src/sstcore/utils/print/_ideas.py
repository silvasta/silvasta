from dataclasses import dataclass
from typing import Any

from rich import inspect
from rich.control import strip_control_codes
from rich.panel import Panel


def test_this_somewhennnn(text: str) -> str:
    """Fix broken or undesired color pattern"""
    inspect(text)  # LATER: inspect rich.inspect
    return strip_control_codes(text)  # COLLECT:


class Dummy:  # COLLECT: parsed name apply
    def log_plain(self, message: str) -> None:
        """Для логов: гарантированно plain-текст, без Rich-тегов."""
        clean = (
            strip_control_codes(message)
            if isinstance(message, str)
            else str(message)
        )
        # Тут можно пробросить в logger.info(clean)
        self._console.print(clean)

    from ..parse.rich_str_name import StyledName

    def styled_name(self, sn: StyledName, **values) -> str:
        """Удобный хелпер: возвращает Rich-строку или plain,  от флага."""
        if self.use_colors:
            return sn.as_rich(**values)
        return sn.as_str(**values)


@dataclass
class PanelStyle:  # COLLECT: panel style DTO
    title: str | None = None
    text_style: str | None = None
    frame: str | None = "cyan"
    padding: tuple = (1, 1)


class BasePrinter:
    def panel(
        self, target: Any, style: PanelStyle | None = None, **kwargs
    ) -> None:
        style = style or PanelStyle()  # Load defaults
        # LATER: the comment below, how to get autocomplete at caller?
        # - import dataclass, init, for sure works. without import?
        # Now you have IDE autocomplete for style.frame, style.title, etc.
        #

    # COLLECT: panel split kwarg trick
    PANEL_KWARGS = {
        "box",
        "safe_box",
        "expand",
        "padding",
        "subtitle",
        "border_style",
    }

    def panel_kw(self, target: Any, **kwargs) -> None:
        # ... pop custom args ...
        # Split kwargs: one dict for Panel, one for the Printer
        p_kwargs = {k: v for k, v in kwargs.items() if k in self.PANEL_KWARGS}
        print_kwargs = {
            k: v for k, v in kwargs.items() if k not in self.PANEL_KWARGS
        }
        panel_obj = Panel(target, **p_kwargs)
        self(
            panel_obj, **print_kwargs
        )  # Now both layers get their specific settings!
