"""
Apply Font Style

                                                       DependencyLevel[0]
"""

from enum import StrEnum, auto


class TextStyle(StrEnum):
    NORMAL = auto()
    BOLD = auto()
    DIM = auto()
    REVERSE = auto()  # renders not nicely...

    # LATER: check:
    # "frame": "frame",
    # "encircle": "encircle",
    # "overline": "overline",

    def to_rich(self) -> str:
        return {
            self.NORMAL: "",
            self.BOLD: "bold",
            self.DIM: "dim",
            self.REVERSE: "reverse",
        }[self]
