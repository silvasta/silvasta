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
from ..utils.path import find_project_root
from ..utils.scanner import TargetFileType


def folder_scanner(  # IMPORTANT: configs from config(derivative?) setup in CLI callback!!!
    scan_root: Path | None = None,
    output_file: Path | None = None,
    print_debug_logs=False,
    path_filter: PathFilter | None = None,
    sort_method: str = "",
):
    """Launch Scanner, then select from Filesystem Tree, finally write to file"""

    scan_root: Path = scan_root or find_project_root()
    output_file: Path = output_file or get_config().paths.summary_file()
    # LATER: check how to apply project.get_config

    output_file: Path = PathGuard.unique(output_file)
    # LATER: maybe some Note when not unique? (maybe inside pathguard)

    path_filter: PathFilter = path_filter or ProjectFilter(
        _debug=print_debug_logs
    )
    # Do this first to avoid error after long selection process
    target: TargetFileType = FolderScanner.target_from_path(output_file)

    scanner: FolderScanner = FolderScanner(
        scan_root=scan_root, path_filter=path_filter
    )
    tree: PathTreeNode = scanner.filesystem_tree()

    # TASK: load selected files here to previous_selection file
    previous_selection: list[Path] = []
    selector = TreeSelectorApp(
        sst_tree=tree, sort_method=sort_method, pre_select=previous_selection
    )
    if selected_files := selector.run():
        printer.lines_with_len(name="Selected Files", lines=selected_files)
        # TASK: cache selected files here to previous_selection file
    else:
        printer.warn("Action cancelled by user.")
        raise typer.Exit()

    data: str = FolderScanner.assemble_summary_file(
        selected_files, target, scan_root=scan_root
    )
    output_file.write_text(data)

    printer.lines(
        header=f"Summary File created! Total Lines: {len(data.splitlines())}",
        lines=[output_file, PathGuard.relative(output_file, strict=False)],
        style="success",
    )


if __name__ == "__main__":
    folder_scanner()
