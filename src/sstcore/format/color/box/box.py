from ....port.view import Stringable
from ._style import TextStyle

type Style = TextStyle | str


class ColorBox:
    """Provide Simple and Fast Color Supply"""

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Colors
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def cyan(self, text: Stringable) -> str:
        return self(text, self._palette.cyan)

    def red(self, text: Stringable) -> str:
        return self(text, self._palette.red)

    def green(self, text: Stringable) -> str:
        return self(text, self._palette.green)

    def yellow(self, text: Stringable) -> str:
        return self(text, self._palette.yellow)

    def blue(self, text: Stringable) -> str:
        return self(text, self._palette.blue)

    def magenta(self, text: Stringable) -> str:
        return self(text, self._palette.magenta)

    def purple(self, text: Stringable) -> str:
        return self(text, "purple")

    def white(self, text: Stringable) -> str:
        return self(text, self._palette.white)

    def black(self, text: Stringable) -> str:
        return self(text, self._palette.black)
