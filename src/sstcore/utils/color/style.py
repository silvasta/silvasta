from enum import StrEnum, auto


class TextStyle(StrEnum):
    # TODO: explain
    NORMAL = auto()
    BOLD = auto()
    DIM = auto()  # LATER: check if or how it is visible in alacritty
    REVERSE = auto()  # вместо INVERT

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
