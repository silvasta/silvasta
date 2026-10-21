"""
Ideas how to combine efficiency with elegance

- Expose attributes simply and efficient with __getattr__,
- Ensure proper type hints, autocomplete and especially:
  --- Warnings for Bad assigned functions ---
- Still show a slim and elegant ColorBox implementation

Things to keep in mind:
- everything stands and falls with the synchronization
"""

from ....port.color import ColorHub, ColorId, Painter
from ....port.represent import Stringable
from ._paint import Paint

class Colors:
    @property
    def hub(self) -> ColorHub: ...
    def paint(self, color: ColorId, /) -> Painter: ...
    def __call__(self, text: Stringable, color: ColorId, /) -> str: ...

    a: Paint
    b: Paint
    c: Paint
    g: Paint
    n: Paint
    o: Paint
    p: Paint
    r: Paint
    s: Paint
    t: Paint
    w: Paint
    y: Paint
    azure: Paint
    blue: Paint
    carbon: Paint
    green: Paint
    black: Paint
    orange: Paint
    purple: Paint
    red: Paint
    slate: Paint
    teal: Paint
    white: Paint
    yellow: Paint
