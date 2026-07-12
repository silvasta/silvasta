"""
Scan Folder and assemble Summary

- use scanner with predefined filter to get Paths
- build PathTree and select from TUI
- write (plain text files) to combined summary file
  - use suffix [.md .txt .xml] to dispatch summary type

"""

import json
from pathlib import Path

import typer

from ...tui import TreeSelectorApp
from ...utils import (
    FolderScanner,
    PathFilter,
    PathGuard,
    PathTreeNode,
    Printer,
    ProjectFilter,
)
from ...utils import printer as backup_printer
from ...utils.scanner import write_summary_file


def folder_scanner(
    scan_root: Path,
    output_file: Path,
    cache_file: Path | None = None,
    sort: str = TreeSelectorApp.Sort.SELECTION,
    printer: Printer | None = None,
    filter: PathFilter | None = None,
):
    """Launch Scanner, select from Filesystem Tree and write to file"""

    output_file: Path = PathGuard.unique(output_file)
    printer: Printer = printer or backup_printer

    if filter is None:  # filter: PathFilter = _setup_filter()
        filter = ProjectFilter(require_all=set(), require_any=set())

    scanner = FolderScanner(scan_root=scan_root, filter=filter)
    tree: PathTreeNode = scanner.tree()
    previous: list[Path] = _load(cache_file, printer) if cache_file else []
    selector = TreeSelectorApp(
        sst_tree=tree, sort_method=sort, pre_select=previous
    )
    if not (selected_files := selector.run()):
        printer.warn("Action cancelled by user.")
        raise typer.Exit()
    printer.lines_with_len(name="Selected Files", lines=selected_files)

    _save(cache_file, selected_files, printer) if cache_file else None
    data: str = write_summary_file(selected_files, output_file)

    printer.lines(
        header=f"Summary File created! Total Lines: {len(data.splitlines())}",
        lines=[output_file, PathGuard.relative(output_file, strict=False)],
        style="green",
    )


def _setup_filter() -> PathFilter:
    # TODO: FilterBox!!!
    # create module inside filter that collects predefined filter,
    # provide together with different options and toggles,
    # -> maybe controlled with tui selector and json cache
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
            ".lua",
        },
    )


def _load(cache_file: Path, printer: Printer) -> list[Path]:
    if cache_file.exists():
        try:
            with open(cache_file, encoding="utf-8") as f:
                paths_str = json.load(f)
                return [Path(p) for p in paths_str if Path(p).exists()]
        except json.JSONDecodeError, OSError:
            printer.warn("Failed to read scanner cache. Starting fresh.")
    return []


def _save(cache_file: Path, selected: list[Path], printer: Printer) -> None:
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump([str(p) for p in selected], f, indent=2)
    except OSError as e:
        printer.warn(f"Could not save selection cache: {e}")


# TASK: db_cache
# def _load(cache_file: Path | None, printer: Printer, scan_root: Path) -> list[Path]:
#     # cache_file игнорируем: теперь всё в SQLite
#     records = get_recent_selections(scan_root=scan_root, limit=1)
#     if not records:
#         return []
#     record = records[0]
#     try:
#         paths_str = json.loads(record.selected_paths)
#         return [Path(p) for p in paths_str if Path(p).exists()]
#     except Exception:
#         printer.warn("Failed to read selection from cache. Starting fresh.")
#         return []
# def _save(cache_file: Path | None, selected: list[Path], printer: Printer, filter_mode=None, extra_inc=None, extra_exc=None):
#     # cache_file игнорируем
#     try:
#         save_selection(
#             scan_root=Path.cwd(),  # или передай из folder_scanner
#             selected=selected,
#             filter_mode=filter_mode,
#             extra_include=extra_inc,
#             extra_exclude=extra_exc,
#         )
#     except Exception as e:
#         printer.warn(f"Could not save selection cache: {e}")


if __name__ == "__main__":
    folder_scanner(scan_root=Path.cwd(), output_file=Path("summary.xml"))
