"""
printer - quick helper copied temporary into port

- temporary module
"""

from sstcore.port.calling import Stringable

__all__: list[str] = [
    "printer",
]

from collections.abc import Iterable
from contextlib import contextmanager

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

console = Console()


class QuickPrinter:
    def __call__(self, *args, **kwargs):
        console.print(*args, **kwargs)

    def lines(self, target: Iterable[Stringable], /):
        match target:
            case dict():
                _lines = (f"{k}: {v}" for k, v in target.items())
            case _:
                _lines = (str(i) for i in target)
        self("\n".join(_lines))

    @contextmanager
    def topic(self, title, /):
        self.panel(f"Start of: {title}", frame="green", title=title)
        try:
            yield
        finally:
            self.line()

    #  LINE: -- Layouts -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def section(self, title, content):
        self.panel(title, frame="yellow")
        self(content)

    def panel(self, content, /, text="bold white", title=None, frame="cyan"):
        panel = Panel(
            renderable=content,
            style=text,
            title=f"[bold white]{title}[/]" if title else None,
            title_align="right",
            border_style=frame,
        )
        self(panel)

    def header(self, content, /, title=None, frame: str = "cyan") -> None:
        self.panel(content, frame=frame, title=title)

    def line(self, char="-- --- --", color="red"):
        self(Rule(style=color, characters=char))

    #  LINE: -- Specialized -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def vars(self, target, /):
        self(vars(target), title=f"vars({clsname(target)})")

    def repr(self, target, /):
        self(repr(target))

    def debug(
        self,
        target: dict,
        /,
        header="Dict Inspection",
        show_type: bool | tuple[bool, bool] = (True, True),
        style="yellow",
    ) -> None:
        """Render colorful Debug Dict, optional with Key or Value Type"""
        if header:
            self.header(header, title="Dict Inspection", frame=style)

        table = Table(style=style)

        show_key_type, show_value_type = (
            show_type
            if isinstance(show_type, tuple)
            else (show_type, show_type)
        )

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


def clsname(target, /, default="") -> str:
    """Extract name from instance or class"""
    default: str = default or type(target).__name__
    return getattr(target, "__name__", default)


printer = QuickPrinter()
