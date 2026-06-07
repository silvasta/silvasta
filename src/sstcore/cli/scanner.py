from pathlib import Path

import typer

from ..config import get_config
from ..tui import TreeSelectorApp
from ..utils import (
    FolderScanner,
    PathFilter,
    PathGuard,
    PathTreeNode,
    ProjectFilter,
    printer,
)
from ..utils.path import get_project_root
from ..utils.scanner import write_summary_file


def folder_scanner(
    scan_root: Path | None = None,
    output_file: Path | None = None,
    filter: PathFilter | None = None,
    sort_method: str = "",
):
    """Launch Scanner, select from Filesystem Tree and write to file"""

    scan_root: Path = scan_root or get_project_root()
    output_file: Path = output_file or get_config().paths.summary_file()
    output_file: Path = PathGuard.unique(output_file)

    if filter is None:
        filter: ProjectFilter = _setup_filter()

    scanner = FolderScanner(scan_root=scan_root, path_filter=filter)
    tree: PathTreeNode = scanner.tree()

    previous_selection: list[Path] = []  # TASK: implement: previous_selection

    selector = TreeSelectorApp(
        sst_tree=tree, sort_method=sort_method, pre_select=previous_selection
    )
    if selected_files := selector.run():  # TASK: cache selected files here
        printer.lines_with_len(name="Selected Files", lines=selected_files)
    else:
        printer.warn("Action cancelled by user.")
        raise typer.Exit()

    data: str = write_summary_file(selected_files, output_file)

    printer.lines(
        header=f"Summary File created! Total Lines: {len(data.splitlines())}",
        lines=[output_file, PathGuard.relative(output_file, strict=False)],
        style="green",
    )


def _setup_filter() -> ProjectFilter:
    return ProjectFilter(
        exclude={
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "env",
            "target",
        },
        require_any={
            ".py",
            ".pyi",
            ".rs",
            ".md",
            ".json",
            ".yaml",
            ".toml",
            ".tex",
            ".cls",
        },
    )


if __name__ == "__main__":
    folder_scanner()
