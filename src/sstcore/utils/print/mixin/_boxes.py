from rich.box import Box


class BoxLibrary:  # IDEA: Enum!! best for select
    """Library of custom Rich Box layouts for the Printer."""

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

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### MINI
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

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
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Special
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    DASH = Box(
        ""
        "╋╸╸╋\n"  # 1. Top border
        "╹  ╹\n"  # 2. Header walls
        "╹  ╹\n"  # 3. Header divider
        "╹  ╹\n"  # 4. Body walls
        "╹  ╹\n"  # 5. Body row divide
        "╹  ╹\n"  # 6. Footer divider
        "╹  ╹\n"  # 7. Footer walls
        "╋╸╸╋\n"  # 8. Bottom border
    )

    EDGE = Box(
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
