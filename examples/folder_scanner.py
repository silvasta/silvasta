from pathlib import Path

from sstcore.utils import FolderScanner, PathGuard, PathTreeNode, printer
from sstcore.utils.path import find_project_root
from sstcore.utils.simple_tree import build_path_tree

SCAN_ROOT: Path = find_project_root()


def main():
    """Task selector"""
    scan_dir()
    # tree_dir_absolute()
    # tree_dir_relative()

    print("done")


def scan_dir():
    absolute_paths: list[Path] = []
    relative_paths: list[Path] = []

    for abs_path in FolderScanner.walk(root=SCAN_ROOT):
        absolute_paths.append(abs_path)
        rel_path: Path = PathGuard.relative(target=abs_path, root=SCAN_ROOT)
        relative_paths.append(rel_path)

    printer.lines_with_len(
        name="Absolute Paths",
        lines=absolute_paths,
    )

    printer.lines_with_len(
        name="Relative Paths",
        lines=relative_paths,
    )


def tree_dir_absolute():
    printer.title("Tree Dir Absolute")
    paths: list[Path] = list(FolderScanner.walk(root=SCAN_ROOT))
    tree: PathTreeNode = build_path_tree(paths)
    printer.tree_graph(tree)


def tree_dir_relative():
    printer.title("Tree Dir Relative")
    paths: list[Path] = FolderScanner(scan_root=SCAN_ROOT).scan_local_files()
    tree: PathTreeNode = build_path_tree(paths, root_name="ProjectRoot")
    printer.tree_graph(tree)


if __name__ == "__main__":
    main()
