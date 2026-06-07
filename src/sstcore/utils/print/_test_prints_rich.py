import fire
from pydantic import BaseModel
from rich.color import ANSI_COLOR_NAMES

# from rich.palette import ColorBox as Rcb
from rich.style import Style

from sstcore import printer


def main():
    fire.Fire(PrintSelection)


class PrintSelection:
    """Collect different Layouts and Functions"""

    def __init__(self):
        # AI: fill the Classes such that this below works
        # printer(target=(rcb := Rcb()))
        printer.dict_table(ANSI_COLOR_NAMES)
        printer(target=(a := AnsiBox()))
        printer.dict_table(Style.STYLE_ATTRIBUTES, show_type=False)
        printer(target=(s := StyleBox()))
        # self.rcb: Any = rcb
        self.a: AnsiBox = a
        self.s: StyleBox = s

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Shuffle
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def ansi(self):
        self.a.ansi()

    def styl(self):
        self.s.styl()

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### ColorBox
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def some(self):
        # f"""Send the {self.__class__.__name__} text here 󰾚󰾚󰾚"""

        printer.c("How will this looock?")
        printer.r(f"Send the {self.__class__.__name__} text here 󰾚󰾚󰾚")

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Constructor and other support methods
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class AnsiBox(BaseModel):
    """create"""

    def ansi(self):
        raise NotImplementedError


class StyleBox(BaseModel):
    "Style.STYLE_ATTRIBUTES"

    def styl(self):
        raise NotImplementedError


if __name__ == "__main__":  # AI: make this as luasnip
    main()
