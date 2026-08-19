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

from ...port.color import (
    ColorAdapter,
    ColorId,
    ColorIndex,
    ColorStacking,
    Paint,
    Stringable,
)

class ColorBox1:
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
    def __getattr__(self, name: str) -> Paint | ColorStacking: ...
    def __call__(self, text: Stringable, color: ColorId) -> str: ...
    def get(self, _target: ColorId) -> Paint: ...

class ColorBox2:
    shortcuts: dict[str, ColorIndex]
    active: ColorAdapter
    stack: Any

    @overload
    def __getattr__(
        self,
        name: Literal[
            "b", "g", "r", "y", "a", "t", "o", "p", "w", "s", "c", "d"
        ],
    ) -> Paint: ...
    @overload
    def __getattr__(self, name: str) -> Paint | ColorStacking: ...
    def __getattr__(self, name: str) -> Any: ...
