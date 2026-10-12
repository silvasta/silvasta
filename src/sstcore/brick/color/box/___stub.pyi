"""
Ideas how to combine efficiency with elegance

- Expose attributes simply and efficient with __getattr__,
- Ensure proper type hints, autocomplete and especially:
  --- Warnings for Bad assinged functions ---
- Still show a slim and elegant ColorBox implementaion

Things to keep in mind:
- everything stands and falls with the synchronization
"""

from typing import Any, Literal, overload

from ....port.color import ColorHub, ColorId, Painter, Stringable
from ._paint import Paint

class ColorBox1:
    @property
    def hub(self) -> ColorHub: ...
    def paint(self, color: ColorId) -> Painter: ...
    def __call__(self, text: Stringable, color: ColorId) -> str: ...

    b: Paint
    g: Paint
    r: Paint
    y: Paint
    a: Paint
    t: Paint
    o: Paint
    p: Paint
    w: Paint
    s: Paint
    c: Paint
    d: Paint

class ColorBox2:
    @property
    def hub(self) -> ColorHub: ...
    def paint(self, color: ColorId) -> Painter: ...
    def __call__(self, text: Stringable, color: ColorId) -> str: ...
    @overload
    def __getattr__(
        self,
        name: Literal[
            "a",
            "b",
            "c",
            "g",
            "n",
            "o",
            "p",
            "r",
            "s",
            "t",
            "w",
            "y",
            "azure",
            "blue",
            "carbon",
            "green",
            "black",
            "orange",
            "purple",
            "red",
            "slate",
            "teal",
            "white",
            "yellow",
        ],
    ) -> Paint: ...
    @overload
    def __getattr__(self, name: str) -> Paint: ...
    # NEXT:def __getattr__(self, name: str) -> Paint | ColorStacking: ...
    def __getattr__(self, name: str) -> Any: ...
