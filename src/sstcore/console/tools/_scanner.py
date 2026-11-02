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

from pathlib import Path

import typer

from ...port.printer import Print
from ...port.scanner import ScanCaching, ScanMode
from ...util.filter import PathFilter, ProjectFilter
from ...util.print import printer as _printer
from ...util.scan import FolderScanner, SummaryFile
from ..select import TreeSelectorApp


def folder_scanner(
    scan_root: Path,
    output_file: Path,
    cache: ScanCaching,
    preset: str | None = None,
    cache_reset: bool = False,
    sort: str = TreeSelectorApp.Sort.SELECTION,
    printer: Print | None = None,
    filter: PathFilter | None = None,
    scan_mode: ScanMode = ScanMode.READ,
):
    """Launch Scanner, select from Filesystem Tree and write to file"""

    printer: Print = printer or _printer

    if filter is None:
        filter = ProjectFilter(require_all=set(), require_any=set())

    target_preset = preset or cache.LAST

    with cache:
        pre_select: list[Path] = (
            [] if cache_reset else cache.load(name=target_preset)
        )
        selector = TreeSelectorApp(
            sst_tree=FolderScanner(scan_root, filter).tree(),
            sort_method=sort,
            pre_select=pre_select,
        )
        if not (selected_files := selector.run()):
            printer.warn("No files selected...")
            raise typer.Exit()

        printer.lines.len("Selected Files", selected_files)
        cache.save(selected_files, name=target_preset)

    printer(
        summary_file := SummaryFile.with_scanner(
            output_file,
            target_files=selected_files,
            local_root=scan_root,
            scan_mode=scan_mode,
        )
    )
    summary_file.write()
    printer.success(
        summary_file.name,
        f"Summary File created! Total Lines: {summary_file.n_lines}",
    )
