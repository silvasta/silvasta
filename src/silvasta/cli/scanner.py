from pathlib import Path

import typer
from loguru import logger

from silvasta.config import get_config
from silvasta.tui.tree_selector import TreeSelectorApp
from silvasta.utils import (
    FolderScanner,
    PathGuard,
    PathTreeNode,
    ProjectFilter,
    printer,
)
from silvasta.utils.path import find_project_root
from silvasta.utils.scanner import TargetFileType


def main(
    scan_root: Path | None = None,
    output_file: Path | None = None,
    print_debug_logs=False,
):
    """Launch Scanner, then select from Filesystem Tree, finally write to file"""

    scan_root: Path = scan_root or find_project_root()
    output_file: Path = output_file or get_config().paths.summary_file()

    scanner: FolderScanner = FolderScanner(
        scan_root=scan_root,
        path_filter=ProjectFilter(_debug=print_debug_logs),
    )
    tree: PathTreeNode = scanner.filesystem_tree()

    tui = TreeSelectorApp(sst_tree=tree)
    selected_files: list[Path] | None = tui.run()

    if not selected_files:
        printer.warn("Action cancelled by user.")
        raise typer.Exit()

    target: TargetFileType = FolderScanner.target_from_path(output_file)

    data: str = FolderScanner.assemble_summary_file(
        selected_files, target, scan_root=scan_root
    )

    PathGuard.unique(output_file).write_text(data)

    logger.info(f"Summary written to: {output_file=}")


if __name__ == "__main__":
    main()
