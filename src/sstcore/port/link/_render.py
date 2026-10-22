"""
Render the Output with Lazy Loaded external Libraries

- rich.(Console.)print: direct feedback inside active terminal session
- loguru: when it needs to be retained for longer than just one window

                               DependencyLevel.sstcore.port.link[1]
"""

from functools import lru_cache
from typing import Any
from weakref import WeakSet

from src.sstcore.port.link._define import Doc

from ._define import LinkRegistry, Param, PortPrinter, SortedDocs


def _loguru(*args: Any, sender: str = "", **kwargs: Any) -> None:
    from loguru import logger

    message: str = " ".join(a if isinstance(a, str) else repr(a) for a in args)
    info: str = ", ".join(f"{k}{v}" for k, v in kwargs.items())
    logger.opt(depth=3).debug(f"[{sender}] {message} ({info})")


def _rich(sender: Any = None, *args: Any, **kwargs: Any) -> None:
    from rich import print as rprint

    prefix: str = f"[bold cyan]{sender}[/] [dim]│[/]"
    rprint(f"[dim]⚡[/]{prefix}", *args, **kwargs)


def _format_cell(val: Any) -> str:
    """Format types, WeakSets, and Docs cleanly for Rich panels and tables."""
    if isinstance(val, type):
        return val.__name__
    if isinstance(val, WeakSet):
        return ", ".join(c.__name__ for c in val) or "∅"
    if isinstance(val, Doc):
        attr_suffix: str = f".{val.attr}" if val.attr else ""
        return f"[bold]{val.source.__name__}{attr_suffix}[/]: {val.text!r}"
    return str(val)


class _NoopPrinter:
    """Zero-cost printer sink when rendering is disabled."""

    def __call__(self, *args, **kwargs): ...
    def line(self, *args, **kwargs): ...
    def panel(self, *args, **kwargs): ...
    def table(self, *args, **kwargs): ...
    def show_sort_result(self, *args, **kwargs): ...
    def overview(self, *args, **kwargs): ...


NOOP_PRINTER: PortPrinter = _NoopPrinter()


@lru_cache(maxsize=1)
def _load_printer() -> PortPrinter:
    """From here Only Printer"""

    from rich.console import Console
    from rich.errors import NotRenderableError
    from rich.panel import Panel
    from rich.table import Table

    class MiniPrinter:
        console = Console()

        def __call__(self, *args, **kwargs):
            try:
                self.console.print(*args, **kwargs)
            except NotRenderableError as error:
                param = Param(args, kwargs)
                self.panel(str(param), title=str(error), color="red")

        def line(self, *target, color: str = "yellow"):
            self("\n".join(str(i) for i in target), style=color)

        def panel(self, *content: Any, title: Any = None, color: str = "cyan"):
            body: str = (
                "\n".join(_format_cell(c) for c in content)
                if content
                else "[dim]Empty[/]"
            )
            panel = Panel(
                renderable=body,
                title=f"[bold white]{title}[/]" if title else None,
                title_align="right",
                border_style=color,
            )
            self(panel)

        def table(
            self,
            target: dict,
            /,
            show_key_type: bool = False,
            show_value_type: bool = False,
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
                    str(key),
                    *([type(key).__name__] if show_key_type else []),
                    str(value),
                    *([type(value).__name__] if show_value_type else []),
                ]
                table.add_row(*row)
            self(table)

        def show_sort_result(  # MOVE: printer?
            self,
            docs: SortedDocs,
            level=2,
            stat="cyan",
            fail="orange_red1",
            port="purple",
            plug="green",
        ):
            if level < 1:
                return

            if not docs:
                self.panel("Nothing to print...", color="blue")
                return

            self.panel(
                f"[{stat}]Statistics[/] {docs!r}", title=docs, color=stat
            )

            if level < 2:
                return

            self.panel(f"[{fail}]Failed[/]", color=fail, title=repr(docs))
            self.panel(*docs.fail, color=fail, title=f"[{fail}]Fails[/]")

            if level < 3:
                return

            self.panel(f"[{port}]PortDocs[/]", color=port, title=repr(docs))
            self.panel(*docs.port, color=port, title=f"[{port}]Protocol[/]")

            self.panel(f"[{plug}]PlugDocs[/]", color=plug, title=repr(docs))
            self.panel(
                *docs.plug, color=plug, title=f"[{plug}]Implementation[/]"
            )

        def overview(self, portlink: Any, registry: LinkRegistry, /):
            self.panel(f"{portlink}::{registry}")
            self.table(dict(registry._by_port))
            self.table(dict(registry._by_plug))

    return MiniPrinter()
