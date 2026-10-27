"""Collect Template for Panel Boxes"""

__all__: list[str] = [
    "Boxes",
    #
    "ROUND",
    "OPEN",
    "UP",
    "DOWN",
    "MINI",
    "MINI_UP",
    "MINI_DOWN",
    "CORNER",
    #
    "BOX_MAP",
]


from rich.box import ROUNDED, Box

from ...port.event._param import _Boxes as Boxes

#  LINE: -- Regular -- -- - -- -- - -- -- - -- -- - -- -- - -- --


CORNER = Box(
    ""
    "┼──┼\n"  # 1. Top border (Crosses at corners, solid horizontal)
    "│  │\n"  # 2. Header walls (Solid vertical)
    "│  │\n"  # 3. Header divider
    "│  │\n"  # 4. Body walls
    "│  │\n"  # 5. Body row divide
    "│  │\n"  # 6. Footer divider
    "│  │\n"  # 7. Footer walls
    "┼──┼\n"  # 8. Bottom border (Crosses at corners, solid horizontal)
)

ROUND: Box = ROUNDED  # Panel Default


#  LINE: -- OPEN -- -- - -- -- - -- -- - -- -- - -- -- - -- --


OPEN = Box(
    ""
    "────\n"  # 1. Top border
    "    \n"  # 2. Header walls
    "    \n"  # 3. Header divider
    "    \n"  # 4. Body walls
    "    \n"  # 5. Body row divider
    "    \n"  # 6. Footer divider
    "    \n"  # 7. Footer walls
    "────\n"  # 8. Bottom border
)

UP = Box(
    ""
    "────\n"  # 1. Top border
    "    \n"  # 2. Header walls
    "    \n"  # 3. Header divider
    "    \n"  # 4. Body walls
    "    \n"  # 5. Body row divider
    "    \n"  # 6. Footer divider
    "    \n"  # 7. Footer walls
    "    \n"  # 8. Bottom border
)

DOWN = Box(
    ""
    "    \n"  # 1. Top border
    "    \n"  # 2. Header walls
    "    \n"  # 3. Header divider
    "    \n"  # 4. Body walls
    "    \n"  # 5. Body row divider
    "    \n"  # 6. Footer divider
    "    \n"  # 7. Footer walls
    "────\n"  # 8. Bottom border
)


#  LINE: -- Mini -- -- - -- -- - -- -- - -- -- - -- -- - -- --


MINI = Box(
    ""
    " ─  \n"  # 1. Top border
    "    \n"  # 2. Header walls
    "    \n"  # 3. Header divider
    "    \n"  # 4. Body walls
    "    \n"  # 5. Body row divide
    "    \n"  # 6. Footer divider
    "    \n"  # 7. Footer walls
    " ─  \n"  # 8. Bottom border
)

MINI_UP = Box(
    ""
    " ─  \n"  # 1. Top border
    "    \n"  # 2. Header walls
    "    \n"  # 3. Header divider
    "    \n"  # 4. Body walls
    "    \n"  # 5. Body row divide
    "    \n"  # 6. Footer divider
    "    \n"  # 7. Footer walls
    "    \n"  # 8. Bottom border
)

MINI_DOWN = Box(
    ""
    "    \n"  # 1. Top border
    "    \n"  # 2. Header walls
    "    \n"  # 3. Header divider
    "    \n"  # 4. Body walls
    "    \n"  # 5. Body row divide
    "    \n"  # 6. Footer divider
    "    \n"  # 7. Footer walls
    " ─  \n"  # 8. Bottom border
)

BOX_MAP: dict[Boxes, Box] = {
    Boxes.CORNER: CORNER,
    Boxes.ROUND: ROUNDED,
    Boxes.OPEN: OPEN,
    Boxes.UP: UP,
    Boxes.DOWN: DOWN,
    Boxes.MINI: MINI,
    Boxes.MINI_UP: MINI_UP,
    Boxes.MINI_DOWN: MINI_DOWN,
}

Boxes.register(BOX_MAP)


if __name__ == "__main__":
    print(Boxes)
    for f in Boxes:
        print(f, f.get())
