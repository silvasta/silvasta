"""
Show Examples of the painted enumerated tuple str ColorRegistry

- TODO: Update this...
  - Wired Painter(str) live in the 3-Enum Grid (color,adapter,palette)
  - Color production, global cache and lookups happen in the Paint Mill
  - Interchangeable Tuple Palettes operated from LightSpectrumDistributor
  - Simple Facade and internal orchestration by the ColorManager, Colors

"""

from contextlib import contextmanager
from pathlib import Path
from typing import Protocol

from fire import Fire
from rich.console import Console

from sstcore.brick.color.box import Colors
from sstcore.brick.color.box._paint import Paint
from sstcore.port.color import Color


def main():
    printy.start(Path(__file__).name)
    Fire(Commands)


class Commands:
    def basic(self):
        basic()


#  LINE: -- Colors -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def basic():
    text = "make me colorful"
    printy(text)

    azure = Paint(Color.AZURE, lambda x: rich_markup(x, "cyan"))

    _check_type = "yes" if isinstance(azure, str) else "no"

    with printy.section("Check Colors"):
        printy(azure(text))

    colors = Colors()
    colors.paint(3)


#  LINE: -- Helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def nop(*_, **__): ...


class Printy:
    """Adapt sstcore.Printer with minimal needed interface"""

    def __init__(self):
        self.console = Console()

    def __call__(self, *args, **kwargs):
        self.console.print(*args, **kwargs)

    @contextmanager
    def section(self, _title: str):
        self.start(_title)
        try:
            yield
        except Exception as error:
            print(f"FAIL for {_title}:", error)
        finally:
            self.separator()

    def start(self, _title):
        self.separator(teal := "bold steel_blue1", a=False)
        start = f"{_r('Start', 'bold black on green')}"
        self(f"{start} {_title}", style=teal)
        self.separator(teal, b=False)

    def separator(self, style="red", /, b=True, a=True):
        self("\n" if b else "", "--- " * 5, "\n" if a else "", style=style)


printy = Printy()


def rich_markup(text: Stringable, style: Stringable = "bold", /):
    return f"[{style}]{text}[/]" if style else text


class Stringable(Protocol):
    def __str__(self): ...


_r = rich_markup

if __name__ == "__main__":
    main()
