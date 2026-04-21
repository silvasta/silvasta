from pathlib import Path

from silvasta.utils import (
    FolderScanner,
    PathGuard,
    PathTreeNode,
    ProjectFilter,
    printer,
)
from silvasta.utils.path import find_project_root
from silvasta.utils.simple_tree import build_path_tree

# SCAN_ROOT: Path = find_project_root() / "src/silvasta"
SCAN_ROOT: Path = find_project_root()


def main():
    """Task selector"""
    # scan_dir()
    # tree_dir_absolute()
    # tree_dir_relative()
    # write_summary()

    print("done")


def scan_dir():
    absolute_paths: list[Path] = []
    relative_paths: list[Path] = []
    for abs_path in FolderScanner.walk(root=SCAN_ROOT):
        absolute_paths.append(abs_path)
        rel_path = PathGuard.compute_relative(target=abs_path, root=SCAN_ROOT)
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


def write_summary(output_filename: str = "summary.md"):

    scanner: FolderScanner = FolderScanner(
        scan_root=SCAN_ROOT,
        path_filter=ProjectFilter(
            # print_debug_logs=True,
            require_any={
                "file_scanner",
                "simple_tree",
                "print",
            },
        ),
    )
    scanner.write_summary_with_name(output_filename)


if __name__ == "__main__":
    main()
