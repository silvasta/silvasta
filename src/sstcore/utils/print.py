from contextlib import contextmanager
from enum import Enum, auto
from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.tree import Tree

from sstcore.utils.simple_tree import SimpleTreeNode


class Printer:
    """Customized Rich Console setup for easy access"""

    _raw_theme: dict[str, str] = {
        "normal": "bold white",
        "info": "black on white",
        "title": "bold white on cyan",
        "warning": "bold white on yellow",
        "success": "bold white on green",
        "danger": "bold black on red",
    }

    project_name: str = "App"
    project_version: str = "0.0.0"

    def __init__(self, custom_theme: dict[str, str] | None = None):
        self.setup_theme(custom_theme)

    class Modus(Enum):
        RICH = auto()
        STANDARD = auto()
        NULL = auto()

    modus: Modus = Modus.RICH

    def __call__(self, *args, **kwargs):
        """Rich console print, printer.mute(): switch to regular print"""
        match self.modus:
            case self.Modus.RICH:
                self.console.print(*args, **kwargs)
            case self.Modus.STANDARD:
                print(args[0] or "something went wrong...")
            case self.Modus.NULL:
                pass

    def unmute(self):
        """Switch to Rich Console Printer"""
        self.modus: self.Modus = self.Modus.RICH

    def to_standard_print(self):
        """Switch to standard Python print"""
        self.modus: self.Modus = self.Modus.STANDARD

    def mute(self):
        """Send all prints to nowhere"""
        self.status: self.Modus = self.Modus.NULL

    @contextmanager
    def muted(self):
        try:
            self.mute()
            yield
        finally:
            self.unmute()

    def setup_theme(self, custom_theme: dict[str, str] | None = None):
        self._raw_theme |= custom_theme or []
        self._rich_theme = Theme(self._raw_theme)
        self.console = Console(theme=self._rich_theme)

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

    def panel(
        self, text: str, title=None, title_align="right", style="", **kwargs
    ):
        title: str | None = title or self.name_and_version() or None
        self(
            Panel(
                renderable=text,
                title=title,
                title_align=title_align,
                style=style,
                **kwargs,
            )
        )

    def title(self, text, *args, **kwargs):
        self.panel(text, *args, **({"style": "title"} | kwargs))

    def warn(self, text, *args, **kwargs):
        self.panel(text, *args, **({"style": "warning"} | kwargs))

    def success(self, text, *args, **kwargs):
        self.panel(text, *args, **({"style": "success"} | kwargs))

    def danger(self, text, *args, **kwargs):
        self.panel(text, *args, **({"style": "danger"} | kwargs))

    def _format(self, target) -> str:
        if isinstance(target, Path):
            if target.is_dir():
                # LATER: fix for relative paths called from different location
                dir_path = f"[bold blue]{target}/[/]"
                file_name = ""
            elif target.parent != Path():
                dir_path = f"[bold blue]{target.parent}/[/]"
                file_name: str = target.name
            else:
                dir_path = ""
                file_name: str = target.name
            return f"{dir_path}{file_name}"  # LATER: color files by type?

        return str(target)

    _inverted_themes: dict[str, str] = {  # TEST: works well?
        "info": "white",
        "title": "cyan",
        "warning": "yellow",
        "success": "green",
        "danger": "red",
    }

    def _match_inverted_style(self, style: str) -> tuple[str, str]:
        if not style:
            return "", ""
        if (header_style := style.lower()) == style:
            return "", style
        if not (line_style := self._inverted_themes.get(header_style)):
            logger.warning(f"No inverted style avaliable: {style=}")
            line_style: str = header_style
        return line_style, header_style

    def lines(self, lines: list, style="", title: str = "", header: str = ""):
        """Print header as title followed by lines in panel"""
        if header:
            style, header_style = self._match_inverted_style(style)
            self.panel(header, style=header_style)
        lines: list[str] = [self._format(line) for line in lines]
        self.panel(text="\n".join(lines), title=title, style=style)

    def lines_with_len(self, name, lines: list, style: str = "title"):
        header = f"{name}: {len(lines)}"
        self.lines(header=header, title=name, lines=lines, style=style)

    def preview_themes(self):
        """Displays all styles in the current theme to visually preview them."""

        self.title("Theme Preview")
        for style in self._rich_theme.styles.keys():
            self(
                f" Style Preview: [ {style} ] ", style=style, justify="center"
            )

    def path_exists_table(self, paths: list[Path], title=None, header="Path"):
        """Check if Paths exist and visualize in Table"""

        table = Table(title=title)
        table.add_column("Status", justify="center")
        table.add_column(header, style="cyan")

        for path in paths:
            status: str = "✅" if path.exists() else ""
            table.add_row(status, self._format(path))  # TEST:

        self(table)

    def dict_table(
        self,
        target: dict,
        header="Dict Inspection",
        key_type=True,
        value_type=True,
    ):
        """Debug Dict"""

        if header is not None:  # Mute header with header=None
            self.title(header, title="Dict Inspection", style="green")

        table = Table(style="cyan")

        table.add_column("Key", justify="left", style="green")
        if key_type:
            table.add_column("Type Key", justify="center", style="magenta")

        table.add_column("Value", style="blue", justify="left")
        if value_type:
            table.add_column("Type Value", style="magenta")

        for key, value in target.items():
            to_print: list[key] = [self._format(key)]
            if key_type:
                to_print.append(self._format(type(key)))
            to_print.append(self._format(value))
            if value_type:
                to_print.append(self._format(type(value)))
            table.add_row(*to_print)

        self(table)

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
