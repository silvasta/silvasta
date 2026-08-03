"""
Mainly for not writing this againg...

-
"""

from sstcore.port.color._palette import ColorPalette


def _store_dict(color: ColorPalette) -> str:
    return {
        ColorPalette.CYAN: "Title",
        ColorPalette.GREEN: "Success",
        ColorPalette.RED: "Warn",
        ColorPalette.YELLOW: "Danger",
        ColorPalette.BLUE: "Path",
        ColorPalette.PURPLE: "Special",
        ColorPalette.BLACK: "Break",
        ColorPalette.WHITE: "Info",
    }[color]


def _store_match(color: ColorPalette):
    match color:
        case color.CYAN:
            "Title"
        case color.GREEN:
            "Success"
        case color.RED:
            "Warn"
        case color.YELLOW:
            "Danger"
        case color.BLUE:
            "Path"
        case color.PURPLE:
            "Special"
        case color.BLACK:
            "Break"
        case color.WHITE:
            "Info"
