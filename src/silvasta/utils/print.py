from collections import defaultdict

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme
from rich.tree import Tree

from silvasta.utils.simple_tree import SimpleTreeNode


class Printer:
    """Customized Rich Console setup for easy acces"""

    _raw_theme: dict[str, str] = {
        "info": "black on white",
        "normal": "white",
        "title": "bold white on cyan",
        "warning": "bold white on yellow",
        "success": "bold white on green",
        "danger": "bold black on red",
    }
    # IDEA: style counter!
    # - count which default/not default used and improve

    project_name: str = "App"
    project_version: str = "unknown"

    _fallback_to_standard_print = False

    def __init__(self, custom_theme: dict[str, str] | None = None):
        self.update_theme_load_console(custom_theme)

    def __call__(self, *args, **kwargs):
        """Rich console print, printer.mute(): swich to regular print"""
        if self._fallback_to_standard_print:
            print(args[0] or "Something went wrong in muting printer...")
        else:
            self.console.print(*args, **kwargs)

    def mute(self):
        """Swich to regular Python print"""
        self._fallback_to_standard_print = True

    def unmute(self):
        """Swich to Rich Console Printer"""
        self._fallback_to_standard_print = False

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
        title: str = title or f"{self.project_name} v{self.project_version}"
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
            # "justify": "center", # INFO: no longer possible/needed after swich from Markdown to Panel
        }
        kwargs = defaults | kwargs  # override defaults
        self.panel(text, *args, **kwargs)

    def warn(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "warning",
            # "justify": "center", # INFO: no longer possible/needed after swich from Markdown to Panel
        }
        kwargs = defaults | kwargs  # override defaults
        self.panel(text, *args, **kwargs)

    def success(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "success",
            # "justify": "center", # INFO: no longer possible/needed after swich from Markdown to Panel
        }
        kwargs = defaults | kwargs
        self.panel(text, *args, **kwargs)

    def danger(self, text, *args, **kwargs):
        defaults: dict[str, str] = {
            "style": "danger",
            # "justify": "center", # INFO: no longer possible/needed after swich from Markdown to Panel
        }
        kwargs = defaults | kwargs
        self.panel(text, *args, **kwargs)

    def lines_from_list(
        self,
        lines: list,
        header: str | None = "",
        title: str = "",
        style: str | None = None,
    ):
        """Print header as title followed by lines in panel"""
        if header is not None:
            self.title(header)
        self.panel(text="\n".join(lines), title=title, style=style)

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
        root_style: str = "bold green",
        node_style: str = "cyan",
    ) -> None:
        """Visualizes a SimpleTreeNode model as a nested Rich Tree"""

        root_label: str = (
            f"[{root_style}]{simple_tree.name}[/{root_style}]"
            if root_style
            else simple_tree.name
        )
        visual_tree = Tree(
            root_label,
            # guide_style="bold black",  # Makes the branching lines dark grey
            hide_root=True,  # Makes the branching lines dark grey
            # style="on white",  # Applies a background color to the whole tree area
        )

        def build_branch(
            node: SimpleTreeNode,
            current_visual_branch: Tree,
            current_depth: int,
        ):
            if max_depth is not None and current_depth >= max_depth:
                return

            for child in node.next:
                child_label = (
                    f"[{node_style}]{child.name}[/{node_style}]"
                    if node_style
                    else child.name
                )
                child_branch: Tree = current_visual_branch.add(child_label)

                build_branch(child, child_branch, current_depth + 1)

        build_branch(simple_tree, visual_tree, current_depth=1)

        self(visual_tree)


printer = Printer()
