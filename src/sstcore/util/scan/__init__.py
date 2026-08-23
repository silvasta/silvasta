"""
# Scanner - Detect the Target!

FolderScanner
- Needs a Target Root and optional a FilterSet to Walk a directory
- Provides Paths, builds a PathTree or creates a SummaryFile.

FileScanner
- Future project: detect the content of files

---

Strategy for Integrated Setup:
- Task starts with 2 independant gathering steps:
  - Get file paths: the easy setup, scan the folders and filter, already implemented
  - Get file content: most simple setup: open file, read, provide str
    - Here the complexity can grow very high... mainly in 2 layers:
      - bit->text: binary files, pdfs, more difficult than just code...
      - text->context: AST, CST, extract the meaning of the scans

  Workflow will be, 1. organize Paths, 2. read data and 3. interprete
  - arbitrary combinations possible:
    - file paths exists already in a registry, file text, just step 3
    - specific format is desired or available, focus on read

That was the incoming side, everything until now was input processing.
- Output is as well intended as 2 layers for now:
  - Display Modus: e.g. existing TUI Monitor, nice base to build further
  - Write Modus: here is safe file system writing implemented, nothing more
    - Ok there exist a summary file writer, much more is maybe not even needed
    - Except for the stub files! unsure if a new utils.write makes sense

Process Managment by Scan - here the Core (maybe implemented as StaticFunc toolkit)
- Some assembled class that controls:
  - the 2 eyes of the system, path finder and the data reader
  - the parsing and that the data actually ends up there
  - finally forward everything to TUI/disk
- config and emitter will arrive from CLI

"""

__all__: list[str] = [
    "FolderScanner",
    "FileScanner",
    "SummaryFile",
    "SummaryFileMachine",
]

from ._file import FileScanner
from ._folder import FolderScanner
from ._summary import SummaryFile, SummaryFileMachine

# LATER: SummaryFile, dataclass with list with lines and optional write path
