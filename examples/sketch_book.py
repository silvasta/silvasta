from collections.abc import Callable
from typing import Any

from sstcore import printer
from sstcore.utils.print import ColorBox
from sstcore.utils.tree import SimpleTreeNode, examples

c: ColorBox = printer.colorbox()


def main():
    select: list[int] = [2, 0, 1]

    functions: list[Callable] = [
        show_tree_graph,
        show_headers,
        show_colors,
        show_attributes,
        test_padding,
        experiment_t_string,
    ]
    printer.panel("blbls lldj", frame="plum1")
    printer.panel("blbls lldj", frame="plum2")
    printer.panel("blbls lldj", frame="plum3")
    printer.panel("blbls lldj", frame="plum4")
    printer.panel("blbls lldj", frame="purple")
    printer.panel("blbls lldj", frame="purple3")

    for run in select:
        functions[run]()


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
    def _show(attribute: str):
        if attribute != "default":
            printer._color_box.set(attribute)
        printer.header(f"This is the {attribute}")

    _show(attribute="default")
    _show(attribute="invert")
    _show(attribute="bold")
    _show(attribute="normal")


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


if __name__ == "__main__":
    main()
