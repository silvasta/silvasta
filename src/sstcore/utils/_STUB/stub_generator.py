from pathlib import Path

# NEXT: something like this, but advanced!

# TASK: Build Generalized and per Target


def generate_stubs():
    colors = [
        "red",
        "green",
        "blue",
        "cyan",
        "magenta",
        "yellow",
        "white",
        "black",
    ]
    modifiers = ["bold", "dim", "underline", "italic"]
    shortcuts = ["r", "g", "b", "a", "w", "d"]

    lines = [
        "from typing import Any, Protocol, overload",
        "from sstcore.port.view import Stringable",
        "",
        "class Coloring(Protocol, str):",
        "    def __call__(self, text: Stringable) -> str: ...",
        '    def listen(self, observer: Any) -> "Coloring": ...',
    ]

    # Add modifiers as properties returning Coloring
    for mod in modifiers:
        lines.append(f'    @property\n    def {mod}(self) -> "Coloring": ...')

    lines.extend(
        [
            "",
            "class ColorBox:",
            "    def __call__(self, text: Stringable, color: str) -> str: ...",
            "    def switch_adapter(self, adapter: Any) -> None: ...",
        ]
    )

    for color in colors + shortcuts + modifiers:
        lines.append(f"    @property\n    def {color}(self) -> Coloring: ...")

    lines.append("    def __getattr__(self, name: str) -> Coloring: ...")

    stub_file = Path("src/sstcore/format/color/box/box.pyi")
    stub_file.write_text("\n".join(lines))
    print(f"Generated {stub_file}")


if __name__ == "__main__":
    generate_stubs()
