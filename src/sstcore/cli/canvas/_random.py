"""
Maybe provide some general (random) dispatch functionalities

- select 1 out of n functions to display
- select pairs
- select sometimes pairs but sometimes arrange otherwise...
"""

import random
from typing import Literal

type ModeType = Literal["up", "down", "all"]  # MOVE: printer.layout?

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Random selector
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# REMOVE: after selection
def get_skewed_pairs() -> tuple[ModeType, ModeType]:
    """Give partially Random modes to compare prints over time"""

    modes: list[ModeType] = ["up", "down", "all"]
    # 1. Pick the first mode completely at random (1/3 chance each)
    first: ModeType = random.choice(modes)

    # 2. Define weights for the second choice based on the first choice.
    # We give the matching mode a 50% weight, and split the remaining 50%
    # between the other two choices (25% each).
    if first == "up":
        weights = [0.50, 0.25, 0.25]  # [up, down, all]
    elif first == "down":
        weights = [0.25, 0.50, 0.25]  # [up, down, all]
    else:  # first == "all"
        weights = [0.25, 0.25, 0.50]  # [up, down, all]

    # 3. Pick the second mode using those weights
    second = random.choices(modes, weights=weights, k=1)[0]

    return first, second


# REMOVE: after selection
mode_1, mode_2 = get_skewed_pairs()
