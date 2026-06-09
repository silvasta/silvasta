import fire
from pydantic import BaseModel, Field
from rich.color import ANSI_COLOR_NAMES
from rich.console import Console
from rich.style import Style
from rich.table import Table


# Simulating sstcore.printer behavior based on your usage
class SSTPrinter:
    def __call__(self, target):
        # Keeps track of target execution or registration if needed
        return target

    def dict_table(self, data: dict, show_type: bool = True):
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Key", style="dim")
        table.add_column("Value")
        if show_type:
            table.add_column("Type")

        for key, value in data.items():
            if show_type:
                table.add_row(str(key), str(value), type(value).__name__)
            else:
                table.add_row(str(key), str(value))
        console.print(table)

    def c(self, text: str):
        Console().print(f"[cyan]{text}[/cyan]")

    def r(self, text: str):
        Console().print(f"[bold red]{text}[/bold red]")


printer = SSTPrinter()


class AnsiBox(BaseModel):
    """Handles ANSI Color operations"""

    color_names: dict = Field(default_factory=lambda: ANSI_COLOR_NAMES)

    def ansi(self):
        """Prints all available ANSI colors elegantly"""
        console = Console()
        for color in self.color_names.keys():
            console.print(f"Color: {color}", style=color)


class StyleBox(BaseModel):
    """Handles Rich Style Attribute operations"""

    style_attrs: dict = Field(
        default_factory=lambda: {
            k: v for k, v in Style.STYLE_ATTRIBUTES.items()
        }
    )

    def do(self):
        """Prints text styles based on attributes"""
        console = Console()
        for attr in self.style_attrs.keys():
            try:
                console.print(
                    f"Testing style attribute: {attr}",
                    style=Style(frame=True if attr == "frame" else None),
                )
            except Exception:
                console.print(f"Attribute available: {attr}")


class PrintSelection:
    """Collect different Layouts and Functions"""

    def __init__(self):
        # AI: Filled classes such that this orchestration chain works perfectly
        printer.dict_table(ANSI_COLOR_NAMES)
        printer(target=(a := AnsiBox()))
        printer.dict_table(Style.STYLE_ATTRIBUTES, show_type=False)
        printer(target=(s := StyleBox()))

        self.a: AnsiBox = a
        self.s: StyleBox = s

    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
    # Shuffle Commands
    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

    def ansi(self):
        """Trigger ANSI styling demonstration"""
        self.a.ansi()

    def do(self):
        """Trigger Style attributes demonstration"""
        self.s.do()

    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
    # ColorBox / Testing
    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

    def some(self):
        """Send the PrintSelection text here 󰾚󰾚󰾚"""
        printer.c("How will this looock?")
        printer.r(f"Send the {self.__class__.__name__} text here 󰾚󰾚󰾚")


def main():
    fire.Fire(PrintSelection)


# AI: Luasnip configuration format for Neovim:
# s("ifmain", fmt([[
# if __name__ == "__main__":
#     {}
# ]], {i(1, "main()")}))
if __name__ == "__main__":
    main()
