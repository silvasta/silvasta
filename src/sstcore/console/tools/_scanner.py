"""
Scan Folder and assemble Summary

- use scanner with predefined filter to get Paths
- build PathTree and select from TUI
- write (plain text files) to combinedsummary_file file
  - use suffix [.md .txt .xml] to dispatchsummary_file type

"""

__all__: list[str] = [
    "folder_scanner",
]

import json
from pathlib import Path

import typer

from ...util import FolderScanner, Printer
from ...util import printer as backup_printer
from ...util.filter import PathFilter, ProjectFilter
from ...util.scan import ScanMode, SummaryFile
from ..select import TreeSelectorApp

# TASK: global setup
# - issue with project root
#   - if not found:
#     - improve fix with HomeSetup
#   - if found:
#     - avoid creating configs there
#     - check if data/summary.md is proper


def folder_scanner(
    scan_root: Path,
    output_file: Path,
    cache_file: Path,
    cache_reset: bool = False,
    sort: str = TreeSelectorApp.Sort.SELECTION,
    local_printer: Printer | None = None,
    filter: PathFilter | None = None,
    scan_mode: ScanMode = ScanMode.RAW,
):
    """Launch Scanner, select from Filesystem Tree and write to file"""

    printer: Printer = local_printer or backup_printer

    if filter is None:
        filter = ProjectFilter(require_all=set(), require_any=set())

    selector = TreeSelectorApp(
        sst_tree=FolderScanner(scan_root, filter).tree(),
        sort_method=sort,
        pre_select=[] if cache_reset else _load_scan(cache_file, printer),
    )
    if not (selected_files := selector.run()):
        printer.warn("No files selected...")
        raise typer.Exit()

    printer.lines_with_len(name="Selected Files", lines=selected_files)
    _save_to_cache(cache_file, selected_files, printer)
    printer(
        target=(
            summary_file := SummaryFile.with_scanner(
                output_file,
                target_files=selected_files,
                local_root=scan_root,
                scan_mode=scan_mode,
            )
        )
    )
    summary_file.write()
    printer.title(
        text=f"Summary File created! Total Lines: {summary_file.n_lines}",
        title=summary_file.name,
        style="green",
    )


def _load_scan(cache_file: Path, printer: Printer) -> list[Path]:
    if cache_file.exists():
        try:
            with open(cache_file, encoding="utf-8") as f:
                paths_str = json.load(f)
                return [Path(p) for p in paths_str if Path(p).exists()]
        except json.JSONDecodeError, OSError:
            printer.warn("Failed to read scanner cache. Starting fresh.")
    return []


def _save_to_cache(
    cache_file: Path, selected: list[Path], printer: Printer
) -> None:
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump([str(p) for p in selected], f, indent=2)
    except OSError as e:
        printer.warn(f"Could not save selection cache: {e}")


if __name__ == "__main__":
    folder_scanner(
        scan_root=Path.cwd(),
        output_file=Path("summary.xml"),
        cache_file=Path(".scanner.json"),
    )
