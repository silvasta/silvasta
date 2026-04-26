from pathlib import Path

import typer

from ..config import get_config
from ..tui import TreeSelectorApp
from ..utils import (
    FolderScanner,
    PathGuard,
    PathTreeNode,
    ProjectFilter,
    printer,
)
from ..utils.path import find_project_root
from ..utils.scanner import TargetFileType


def main(
    scan_root: Path | None = None,
    output_file: Path | None = None,
    print_debug_logs=False,
):
    """Launch Scanner, then select from Filesystem Tree, finally write to file"""

    scan_root: Path = scan_root or find_project_root()
    output_file: Path = output_file or get_config().paths.summary_file()
    # LATER: check how to apply project.get_config

    output_file: Path = PathGuard.unique(output_file)
    # LATER: maybe some Note when not unique? (maybe inside pathguard)

    # Do this first to avoid error after long selection process
    target: TargetFileType = FolderScanner.target_from_path(output_file)

    scanner: FolderScanner = FolderScanner(
        scan_root=scan_root,
        path_filter=ProjectFilter(_debug=print_debug_logs),
    )
    tree: PathTreeNode = scanner.filesystem_tree()

    if selected_files := TreeSelectorApp(sst_tree=tree).run():
        printer.lines_with_len(
            name="Selected Files",
            lines=selected_files,
        )
    else:
        printer.warn("Action cancelled by user.")
        raise typer.Exit()

    data: str = FolderScanner.assemble_summary_file(
        selected_files, target, scan_root=scan_root
    )
    output_file.write_text(data)

    printer.success(f"Summary written to: {output_file}")


if __name__ == "__main__":
    main()
