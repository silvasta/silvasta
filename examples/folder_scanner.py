from pathlib import Path

from sstcore.config import get_config
from sstcore.utils import (
    FolderScanner,
    PathGuard,
    PathTreeNode,
    ProjectFilter,
    printer,
)
from sstcore.utils.path import find_project_root
from sstcore.utils.simple_tree import build_path_tree

# SCAN_ROOT: Path = find_project_root() / "src/sstcore"
SCAN_ROOT: Path = find_project_root()


def main():
    """Task selector"""
    # scan_dir()
    # tree_dir_absolute()
    # tree_dir_relative()
    write_summary()

    print("done")


def scan_dir():
    absolute_paths: list[Path] = []
    relative_paths: list[Path] = []
    for abs_path in FolderScanner.walk(root=SCAN_ROOT):
        absolute_paths.append(abs_path)
        rel_path = PathGuard.relative(target=abs_path, root=SCAN_ROOT)
        relative_paths.append(rel_path)

    printer._lines_from_list_len(
        name="Absolute Paths",
        lines=[str(path) for path in absolute_paths],
        style="normal",
    )

    printer._lines_from_list_len(
        name="Relative Paths",
        lines=[str(path) for path in relative_paths],
    )


def tree_dir_absolute():

    paths: list[Path] = list(FolderScanner.walk(root=SCAN_ROOT))

    tree: PathTreeNode = build_path_tree(paths)

    printer.tree_graph(tree)


def tree_dir_relative():

    root_name: str = "ProjectRoot"

    paths: list[Path] = FolderScanner(scan_root=SCAN_ROOT).scan_local_files()

    tree: PathTreeNode = build_path_tree(paths, root_name)

    printer.tree_graph(tree)


def write_summary(print_debug_logs=False):

    output_file: str = get_config().paths.summary_file()

    scanner: FolderScanner = FolderScanner(
        scan_root=SCAN_ROOT,
        path_filter=ProjectFilter(
            _debug=print_debug_logs,
            require_any={
                "paths",
                "names",
            },
        ),
    )
    scanner.write_summary_with_name(output_file)


if __name__ == "__main__":
    main()
