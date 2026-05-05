from contextlib import contextmanager
from enum import Enum, auto

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme
from rich.tree import Tree

from sstcore.utils.simple_tree import SimpleTreeNode


class Printer:
    """Customized Rich Console setup for easy access"""

    _raw_theme: dict[str, str] = {
        "info": "black on white",
        "normal": "white",
        "title": "bold white on cyan",
        "warning": "bold white on yellow",
        "success": "bold white on green",
        "danger": "bold black on red",
    }

    project_name: str = "App"
    project_version: str = "0.0.0"

    class Status(Enum):
        RICH = auto()
        REGULAR = auto()
        NULL = auto()

    status: Status = Status.RICH

    _fallback_to_standard_print = False

    def __init__(self, custom_theme: dict[str, str] | None = None):
        self.update_theme_load_console(custom_theme)

    def __call__(self, *args, **kwargs):
        """Rich console print, printer.mute(): switch to regular print"""
        match self.status:
            case self.Status.RICH:
                self.console.print(*args, **kwargs)
            case self.Status.REGULAR:
                if self._fallback_to_standard_print:
                    print(args[0] or "something went wrong...")
            case self.Status.NULL:
                pass

    def unmute(self):
        """Switch to Rich Console Printer"""
        self.status: Printer.Status = self.Status.RICH

    def print_regular(self):
        """Switch to regular Python print"""
        self.status: Printer.Status = self.Status.REGULAR

    def mute(self):
        """Send all prints to nowhere"""
        self.status: Printer.Status = self.Status.NULL

    @contextmanager
    def muted(self):
        try:
            self.mute()
            yield
        finally:
            self.unmute()

    @property
    def name_and_version(self) -> str:
        parts: list[str] = []
        if self.project_name:
            parts.append(self.project_name)
        if self.project_version:
            if self.project_version.startswith("v"):
                parts.append(self.project_version)
            else:
                parts.append(f"v{self.project_version}")
        return " ".join(parts) if parts else ""

    def md(self, text, *args, header: int = 0, **kwargs):
        """Markdown printer, modify first line with header section depth"""

        if not (0 <= header <= 6):  # Generate Header if argument is set
            fallback_header = 0
            self(
                f"Markdown Header {header=} invalid (H1 to H6), using {fallback_header=}",
                style="danger",
            )
            header: int = fallback_header
        prefix: str = f"{'#' * header} " if header > 0 else ""

        kwargs.setdefault("style", "info")

        self(Markdown(f"{prefix}{text}"), *args, **kwargs)

    def panel(self, text: str, title=None, title_align="right", style="info"):
        title: str | None = title or self.name_and_version or None
        self(
            Panel(
                renderable=text,
                title=title,
                title_align=title_align,
                style=style,
            )
        )

    def title(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "title",
        }
        kwargs = defaults | kwargs  # override defaults
        self.panel(text, *args, **kwargs)

    def warn(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "warning",
        }
        kwargs = defaults | kwargs  # override defaults
        self.panel(text, *args, **kwargs)

    def success(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "success",
        }
        kwargs = defaults | kwargs
        self.panel(text, *args, **kwargs)

    def danger(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "danger",
        }
        kwargs = defaults | kwargs
        self.panel(text, *args, **kwargs)

    def lines(
        self,
        lines: list,
        header: str | None = "",
        title: str = "",
        style: str = "info",
    ):
        """Print header as title followed by lines in panel"""
        if header is not None:  # Mute header banner with header=None
            self.title(header)

        lines: list[str] = [str(line) for line in lines]
        # LATER: other formatting to apply?

        self.panel(text="\n".join(lines), title=title, style=style)

    def lines_with_len(self, name, lines: list, style: str = "info"):
        self.lines(
            header=f"{name}: {len(lines)}",
            title=name,
            lines=lines,
            style=style,
        )

    def update_theme_load_console(
        self, custom_theme: dict[str, str] | None = None
    ):
        """Override current theme with custom_theme and attach to console"""
        if custom_theme:
            self._raw_theme |= custom_theme

        self._rich_theme = Theme(self._raw_theme)
        self.console = Console(theme=self._rich_theme)

    def preview_themes(self):
        """Displays all styles in the current theme to visually preview them."""

        self.title("Theme Preview")
        for style in self._rich_theme.styles.keys():
            self(
                f" Style Preview: [ {style} ] ", style=style, justify="center"
            )

    def tree_graph(
        self,
        simple_tree: SimpleTreeNode,
        max_depth: int | None = None,
        root_style: str = "bold magenta",
        node_style: str = "by_level",
        guide_style="bold white",
        hide_root=False,
    ) -> None:
        """Visualizes a SimpleTreeNode model as a nested Rich Tree"""

        _node_styles: dict[int, str] = {
            1: "green",
            2: "yellow",
            3: "white",
        }

        def _apply_style(node_label: str, color: str | int = ""):
            if isinstance(color, int):
                color: str = _node_styles.get(color, "red")
            return f"[{color}]{node_label}[/]" if color else node_label

        visual_tree = Tree(
            label=_apply_style(simple_tree.name, color=root_style),
            guide_style=guide_style,
            hide_root=hide_root,
            # style="on white",  # Applies a background color to the whole tree area
        )

        def build_branch(
            node: SimpleTreeNode,
            current_branch: Tree,
            current_depth: int,
        ):
            if max_depth is not None and current_depth >= max_depth:
                return

            nonlocal node_style
            color: str | int = (
                current_depth if node_style == "by_level" else node_style
            )

            for branch in node.branches:
                child_label: str = _apply_style(
                    branch.display_label, color=color
                )
                child_branch: Tree = current_branch.add(child_label)

                build_branch(branch, child_branch, current_depth + 1)

        build_branch(simple_tree, visual_tree, current_depth=1)

        self(visual_tree)


printer = Printer()

if __name__ == "__main__":
    printer.preview_themes()
