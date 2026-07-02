from collections.abc import Callable
from typing import Any

from loguru import logger
from rich.color import ANSI_COLOR_NAMES, Color
from rich.style import Style

from sstcore import printer
from sstcore.utils.color import ColorBox
from sstcore.utils.color.style import TextStyle
from sstcore.utils.tree import SimpleTreeNode, examples

c: ColorBox = printer.color_box


def main():  # LATER: use fire.Fire for cli?
    """Dispatch tasks with manual index"""

    select: list[int] = []

    select.extend([-1])  # INFO: toggle by comment # (delete and see the issue)

    functions: list[Callable] = [
        show_tree_graph,
        show_headers,
        show_colors,
        show_attributes,
        test_padding,
        experiment_t_string,
        show_all_rich_colors,  # INFO: good one
        show_rich_style_attributes,
        rich_by_number,
    ]

    # LATER: Use ListSelector? maybe optional

    for run in select:
        functions[run]()

    if not select:
        latest()


def latest():
    printer.title("hello")


def dip_example():
    # TODO: transform dip to arg that affects frame,head color but not text
    printer.dip("Sachmis", "sent as the Eye", color="cyan")
    printer.dip("Targets Destoyed", "area cleared", color="green")
    printer.dip("thunder", "is comming", color="yellow")
    printer.dip("Fire", "no regret and forward", color="red")


def rich_by_number():
    rich_default_color: Color = Color.default()
    printer(rich_default_color)
    # TODO: extract rgb below for sst_colorbox.purple
    # -> or use the nvim-todo colors?
    printer(Color.from_rgb(red=124, green=58, blue=237))
    printer(Color.from_ansi(129))
    printer(Color.from_ansi(6))
    printer.dip("PPPPPPPPPPPPPP", "hello", "cyan")


def show_rich_style_attributes():
    printer(rich_styles_raw)
    printer.panel("test")
    printer.dict_table(rich_styles_raw)
    rich_styles: list[str] = list(set(rich_styles_raw.values()))
    for style in rich_styles:
        example: str = f"This is how '{style}' Text looks"
        target = f"Style: {style} - Example: [{style}]{example}[/]"
        printer.panel(target)
        printer(target)


def show_all_rich_colors():
    logger.remove()
    example: str = "This is how colored Text looks"
    for color in rich_colors.keys():
        target = f"{color} - {c(example, color)}"
        printer.panel(target, frame=color)


def show_tree_graph():
    printer.title("Print the SimpleTree", title="SimpleTree")
    example_tree: SimpleTreeNode = examples.simple_tree()
    printer.tree_graph(example_tree)
    printer.tree_graph(examples.big_tree())


def show_headers(text="Selected Models"):
    printer("Default header without extra args")
    printer.header(text)

    printer("predefined setups")
    printer.title(text)
    printer.success(text)
    printer.danger(text)
    printer.warn(text)


def show_colors():
    colors: list[Callable[[Any], None]] = [
        printer.blue,
        printer.red,
        printer.green,
        printer.cyan,
        printer.magenta,
        printer.yellow,
        printer.black,
        printer.white,
    ]
    for color_print in colors:
        printer(f"{color_print.__name__.capitalize():>7}", end=" ")  # ty:ignore
        color_print("This is so Colorful")


def show_attributes():
    for style in TextStyle:
        printer.color_box.switch(style=style)
        printer.header(f"This is the {style}")
        printer.cyan(style)


def test_padding(pad=(1, 3)):

    items: list[str] = ["Original Banner" for _ in range(10)]

    text: str = "\n".join(items)

    printer.banner(target=text, padding=pad)


def experiment_t_string():
    name = "Alice"
    tmpl = t"Hello {name}!"

    # IDEA: use something like this to "de-"colorize strings that do go log

    for s, v in zip(tmpl.strings, tmpl.values, strict=False):
        print(s)
        print(v)
        s + str(v)

    items: zip[tuple[str, Any]] = zip(tmpl.strings, tmpl.values, strict=False)
    result: str = "".join(s + str(v) for s, v in items) + tmpl.strings[-1]

    printer(result)


_this_is = Style.STYLE_ATTRIBUTES
rich_styles_raw: dict[str, str] = {
    "dim": "dim",
    "d": "dim",
    "bold": "bold",
    "b": "bold",
    "italic": "italic",
    "i": "italic",
    "underline": "underline",
    "u": "underline",
    "blink": "blink",
    "blink2": "blink2",
    "reverse": "reverse",
    "r": "reverse",
    "conceal": "conceal",
    "c": "conceal",
    "strike": "strike",
    "s": "strike",
    "underline2": "underline2",
    "uu": "underline2",
    "frame": "frame",
    "encircle": "encircle",
    "overline": "overline",
    "o": "overline",
}


_this_is = ANSI_COLOR_NAMES
rich_colors: dict[str, int] = {
    "aquamarine1": 122,
    "aquamarine3": 79,
    "black": 0,
    "blue": 4,
    "blue1": 21,
    "blue3": 20,
    "blue_violet": 57,
    "bright_black": 8,
    "bright_blue": 12,
    "bright_cyan": 14,
    "bright_green": 10,
    "bright_magenta": 13,
    "bright_red": 9,
    "bright_white": 15,
    "bright_yellow": 11,
    "cadet_blue": 73,
    "chartreuse1": 118,
    "chartreuse2": 112,
    "chartreuse3": 76,
    "chartreuse4": 64,
    "cornflower_blue": 69,
    "cornsilk1": 230,
    "cyan": 6,
    "cyan1": 51,
    "cyan2": 50,
    "cyan3": 43,
    "dark_blue": 18,
    "dark_cyan": 36,
    "dark_goldenrod": 136,
    "dark_green": 22,
    "dark_khaki": 143,
    "dark_magenta": 91,
    "dark_olive_green1": 192,
    "dark_olive_green2": 155,
    "dark_olive_green3": 149,
    "dark_orange": 208,
    "dark_orange3": 166,
    "dark_red": 88,
    "dark_sea_green": 108,
    "dark_sea_green1": 193,
    "dark_sea_green2": 157,
    "dark_sea_green3": 150,
    "dark_sea_green4": 71,
    "dark_slate_gray1": 123,
    "dark_slate_gray2": 87,
    "dark_slate_gray3": 116,
    "dark_turquoise": 44,
    "dark_violet": 128,
    "deep_pink1": 199,
    "deep_pink2": 197,
    "deep_pink3": 162,
    "deep_pink4": 125,
    "deep_sky_blue1": 39,
    "deep_sky_blue2": 38,
    "deep_sky_blue3": 32,
    "deep_sky_blue4": 25,
    "dodger_blue1": 33,
    "dodger_blue2": 27,
    "dodger_blue3": 26,
    "gold1": 220,
    "gold3": 178,
    "gray0": 16,
    "gray100": 231,
    "gray11": 234,
    "gray15": 235,
    "gray19": 236,
    "gray23": 237,
    "gray27": 238,
    "gray3": 232,
    "gray30": 239,
    "gray35": 240,
    "gray37": 59,
    "gray39": 241,
    "gray42": 242,
    "gray46": 243,
    "gray50": 244,
    "gray53": 102,
    "gray54": 245,
    "gray58": 246,
    "gray62": 247,
    "gray63": 139,
    "gray66": 248,
    "gray69": 145,
    "gray7": 233,
    "gray70": 249,
    "gray74": 250,
    "gray78": 251,
    "gray82": 252,
    "gray84": 188,
    "gray85": 253,
    "gray89": 254,
    "gray93": 255,
    "green": 2,
    "green1": 46,
    "green3": 40,
    "green4": 28,
    "green_yellow": 154,
    "grey0": 16,
    "grey100": 231,
    "grey11": 234,
    "grey15": 235,
    "grey19": 236,
    "grey23": 237,
    "grey27": 238,
    "grey3": 232,
    "grey30": 239,
    "grey35": 240,
    "grey37": 59,
    "grey39": 241,
    "grey42": 242,
    "grey46": 243,
    "grey50": 244,
    "grey53": 102,
    "grey54": 245,
    "grey58": 246,
    "grey62": 247,
    "grey63": 139,
    "grey66": 248,
    "grey69": 145,
    "grey7": 233,
    "grey70": 249,
    "grey74": 250,
    "grey78": 251,
    "grey82": 252,
    "grey84": 188,
    "grey85": 253,
    "grey89": 254,
    "grey93": 255,
    "honeydew2": 194,
    "hot_pink": 206,
    "hot_pink2": 169,
    "hot_pink3": 168,
    "indian_red": 167,
    "indian_red1": 204,
    "khaki1": 228,
    "khaki3": 185,
    "light_coral": 210,
    "light_cyan1": 195,
    "light_cyan3": 152,
    "light_goldenrod1": 227,
    "light_goldenrod2": 222,
    "light_goldenrod3": 179,
    "light_green": 120,
    "light_pink1": 217,
    "light_pink3": 174,
    "light_pink4": 95,
    "light_salmon1": 216,
    "light_salmon3": 173,
    "light_sea_green": 37,
    "light_sky_blue1": 153,
    "light_sky_blue3": 110,
    "light_slate_blue": 105,
    "light_slate_gray": 103,
    "light_slate_grey": 103,
    "light_steel_blue": 147,
    "light_steel_blue1": 189,
    "light_steel_blue3": 146,
    "light_yellow3": 187,
    "magenta": 5,
    "magenta1": 201,
    "magenta2": 200,
    "magenta3": 164,
    "medium_orchid": 134,
    "medium_orchid1": 207,
    "medium_orchid3": 133,
    "medium_purple": 104,
    "medium_purple1": 141,
    "medium_purple2": 140,
    "medium_purple3": 98,
    "medium_purple4": 60,
    "medium_spring_green": 49,
    "medium_turquoise": 80,
    "medium_violet_red": 126,
    "misty_rose1": 224,
    "misty_rose3": 181,
    "navajo_white1": 223,
    "navajo_white3": 144,
    "navy_blue": 17,
    "orange1": 214,
    "orange3": 172,
    "orange4": 94,
    "orange_red1": 202,
    "orchid": 170,
    "orchid1": 213,
    "orchid2": 212,
    "pale_green1": 156,
    "pale_green3": 114,
    "pale_turquoise1": 159,
    "pale_turquoise4": 66,
    "pale_violet_red1": 211,
    "pink1": 218,
    "pink3": 175,
    "plum1": 219,
    "plum2": 183,
    "plum3": 176,
    "plum4": 96,
    "purple": 129,
    "purple3": 56,
    "purple4": 55,
    "red": 1,
    "red1": 196,
    "red3": 160,
    "rosy_brown": 138,
    "royal_blue1": 63,
    "salmon1": 209,
    "sandy_brown": 215,
    "sea_green1": 85,
    "sea_green2": 83,
    "sea_green3": 78,
    "sky_blue1": 117,
    "sky_blue2": 111,
    "sky_blue3": 74,
    "slate_blue1": 99,
    "slate_blue3": 62,
    "spring_green1": 48,
    "spring_green2": 47,
    "spring_green3": 41,
    "spring_green4": 29,
    "steel_blue": 67,
    "steel_blue1": 81,
    "steel_blue3": 68,
    "tan": 180,
    "thistle1": 225,
    "thistle3": 182,
    "turquoise2": 45,
    "turquoise4": 30,
    "violet": 177,
    "wheat1": 229,
    "wheat4": 101,
    "white": 7,
    "yellow": 3,
    "yellow1": 226,
    "yellow2": 190,
    "yellow3": 184,
    "yellow4": 106,
}

if __name__ == "__main__":
    main()
