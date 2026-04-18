from pathlib import Path

from silvasta.utils.scanner import FolderScanner

name = "sstcore/src/silvasta"

scan_root: Path = Path.home() / name

scanner = FolderScanner(scan_root)

print(scanner.write_summary_with_name("summary.md"))

print(scan_root.parts)

#
