"""
Show Examples of the painted enumerated tuple str ColorRegistry

- Wired Painter(str) live in the 3-Enum Grid (color,adapter,palette)
- Color production, global cache and lookups happen in the Paint Mill
- Interchangeable Tuple Palettes operated from LightSpectrumDistributor
- Simple Facade and internal orchestration by the ColorManager, Colors

"""

from collections.abc import Generator
from contextlib import contextmanager

from fire import Fire
from rich.console import Console


def main():
    printer.section("Start of name_parsing")
    Fire(ParseTasks)


class ParseTasks:
    """OUTDATED..."""

    def schema(self):
        pass


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Printer:
    def __init__(self):
        self.console = Console()

    @contextmanager
    def section(self, _title: str) -> Generator:
        self.start(_title)
        try:
            yield
        except Exception as error:
            print(f"FAIL for {_title}:", error)
        finally:
            self.separator()

    def start(self, _title):
        start = f"{_r('Start', 'steel_blue1')}"
        self.console.print(f"{start} {_title}", style="cyan")

    def separator(self):
        print("\n---\n")


printer = Printer()


def rich_markup(text: Stringable, style: Stringable = "bold"):
    return f"[{style}]{text}[/]" if style else text


_r = rich_markup
