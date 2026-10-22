"""
Render the Output with Lazy Loaded external Libraries

- rich.(Console.)print: direct feedback inside active terminal session
- loguru: when it needs to be retained for longer than just one window

                               DependencyLevel.sstcore.port.link[1]
"""

from typing import TYPE_CHECKING, Any

from ._define import PortEmit, PortPrinter


def _loguru(*args: Any, sender: str = "", **kwargs: Any) -> None:
    from loguru import logger

    message: str = " ".join(a if isinstance(a, str) else repr(a) for a in args)
    info: str = ", ".join(f"{k}{v}" for k, v in kwargs.items())
    logger.opt(depth=3).debug(f"[{sender}] {message} ({info})")


def _rich(sender: Any = None, *args: Any, **kwargs: Any) -> None:
    from rich import print as rprint

    prefix: str = f"[bold cyan]{sender}[/] [dim]│[/]"
    rprint(f"[dim]⚡[/]{prefix}", *args, **kwargs)


if TYPE_CHECKING:
    _l: PortEmit = _loguru
    _p: PortEmit = _rich


def _load_printer() -> PortPrinter:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    class MiniPrinter:
        console = Console()

        def __call__(self, *args, **kwargs):
            self.console.print(*args, **kwargs)

        def line(self, *target, color: str = "yellow"):
            self("\n".join(str(i) for i in target), color=color)

        def panel(self, content, /, title=None, color="cyan"):
            panel = Panel(
                renderable=content,
                title=f"[bold white]{title}[/]" if title else None,
                title_align="right",
                border_style=color,
            )
            self(panel)

        def table(
            self,
            target: dict,
            show_key_type: bool = False,
            show_value_type: bool = True,
            /,
            color: str = "green",
        ) -> None:
            """Render colorful Debug Dict, optional with Key or Value Type"""

            table = Table(style=color)

            table.add_column("Key", justify="left", style="green")
            if show_key_type:
                table.add_column("Type Key", justify="center", style="magenta")

            table.add_column("Value", style="blue", justify="left")
            if show_value_type:
                table.add_column("Type Value", style="magenta")

            for key, value in target.items():
                row: list[str] = [
                    key,
                    *([type(key).__name__] if show_key_type else []),
                    str(value),
                    *([type(value).__name__] if show_value_type else []),
                ]
                table.add_row(*row)
            self(table)

    if TYPE_CHECKING:
        _printer: PortPrinter = MiniPrinter()

    return MiniPrinter()


class _NoopPrinter:
    """Zero-cost printer sink when rendering is disabled."""

    def __call__(self, *args, **kwargs) -> None: ...
    def line(self, *args, **kwargs) -> None: ...
    def panel(self, *args, **kwargs) -> None: ...
    def table(self, *args, **kwargs) -> None: ...


NOOP_PRINTER: PortPrinter = _NoopPrinter()
