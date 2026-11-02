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
from ...util.filter import PathFilter
from ...util.scan import FolderScanner, SummaryFile
from ..select import TreeSelectorApp


def folder_scanner(
    scan_root: Path,
    output_file: Path,
    cache: ScanCaching,
    filter: PathFilter,
    printer: Print,
    preset: str = "",
    load_cache: bool = False,
    sort: str = TreeSelectorApp.Sort.SELECTION,
    scan_mode: ScanMode = ScanMode.READ,
):
    """Launch Scanner, select from Filesystem Tree and write to file"""

    with cache:
        pre_select: list[Path] = (
            [] if not load_cache else cache.load(name=preset)
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
        # NEXT: ask for preset storage (including name)! here? after which prints?
        new_preset_name: str = input("new preset name: ")
        # LATER: something with timestamp?
        cache.save(selected_files, name=new_preset_name)
        # LATER: print preset save success

    printer(  # LATER: remove, or by toggle?
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
