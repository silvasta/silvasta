"""
The Docstring Merging Render Engine

- Setup prepared with possibilities to grow

                               DependencyLevel.sstcore.port.link[2]
"""

import enum as _e
from collections.abc import Iterable
from contextlib import contextmanager
from typing import Any

from ..calling import Stringable
from ..solid import EnumMachine
from ._define import LinkSpec
from ._model import Doc, Docs, PlugDoc, PortDoc, SidePolicy

printer: Any = None


class MergeMachine(EnumMachine):
    Schema1 = _e.auto()

    def __call__(self, docs: Docs, spec: LinkSpec | None = None) -> str:

        _spec_to_emit_and_format: LinkSpec = spec or LinkSpec()
        port: list[Doc] = []
        plug: list[Doc] = []
        fail: list[Doc] = []
        for doc in docs:
            global printer  # INFO: temporary workaround
            if printer is None:
                printer = _load_printer()
            printer.line(color="cyan")
            match doc:
                case PortDoc():
                    self.sort_for_port(doc, port, fail)
                case PlugDoc():
                    self.sort_for_plug(doc, plug, fail)
        self.handle_sort(port, plug, fail)
        match self:
            case self.Schema1:
                lines: list[str] = self.schema1(port, plug)
                return "\n".join(lines)
        raise NotImplementedError

    def schema1(self, port: list[Doc], plug: list[Doc]) -> list[str]:
        lines: list[str] = []
        if port:
            first, *remaining = port
            self.format_port_header(first, lines)
            self.format_port_body(remaining, lines)
        if plug:
            self.format_separator(lines)
            self.format_plug_body(plug, lines)
        printer.panel(f"Statsistic: Total (multi) lines: {len(lines)}")
        return lines

    def format_port_header(self, first: Doc, lines: list[str]):
        lines.append(first.text.strip("\n"))
        printer(f"Attached Port header: {first.key}")

    def format_port_body(self, remaining: list[Doc], lines: list[str]):
        for doc in remaining:
            lines.append("\n")
            attr_draw: str = f".{doc.attr}" if doc.attr else ""
            lines.append(f"[{doc.source.__name__}{attr_draw}]")
            lines.append(doc.text.strip("\n"))

    def format_separator(self, lines):
        lines.append("\n\n", "--- -- ---" * 8, "\n\n", "Implementation", "\n")

    def format_plug_body(self, plug: list[Doc], lines: list[str]):
        for doc in plug[::-1]:  # CHECK: reverse
            lines.append("\n")
            attr_draw: str = f".{doc.attr}" if doc.attr else ""
            lines.append(f"[{{{doc.source.__name__}}}{attr_draw}]")
            lines.append(doc.text.strip("\n"))

    def handle_sort(self, port: list[Doc], plug: list[Doc], fail: list[Doc]):
        printer.panel(
            f"Stats: port: {len(port)}, plug: {len(plug)}, fail: {len(fail)} "
        )
        if not plug:
            printer.panel("Implementation", frame="yellow", title="Missing")
        if not port:
            printer.panel("Definitions", frame="orange", title="Missing")
        if fail:
            printer.panel(*fail, frame="red", title="Failed")

    def sort_for_port(self, doc: Doc, port: list, fail: list) -> None:
        if SidePolicy.PORT.validate(doc):
            port.append(doc)
            printer(f"Accepted: {doc.key}")
        else:
            fail.append(doc)
            printer(f"Rejected: {doc.key}")

    def sort_for_plug(self, doc: Doc, plug: list, fail: list) -> None:
        if SidePolicy.PLUG.validate(doc):
            plug.append(doc)
            printer(f"Accepted: {doc.key}")
        else:
            fail.append(doc)
            printer(f"Rejected: {doc.key}")


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _load_printer():
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    from rich.table import Table

    class QuickPrinter:
        console = None

        def __call__(self, *args, **kwargs):
            if self.console is None:
                _load_printer()
                self.console = Console()
            self.console.print(*args, **kwargs)

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

        def panel(
            self, content, /, text="bold white", title=None, frame="cyan"
        ):
            panel = Panel(
                renderable=content,
                style=text,
                title=f"[bold white]{title}[/]" if title else None,
                title_align="right",
                border_style=frame,
            )
            self(panel)

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
                self.panel(header, title="Dict Inspection", frame=style)
            show_key_type, show_value_type = (
                show_type
                if isinstance(show_type, tuple)
                else (show_type, show_type)
            )
            table = Table(style=style)
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

    return QuickPrinter()
