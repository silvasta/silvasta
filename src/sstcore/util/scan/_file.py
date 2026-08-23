"""
Scan File Content

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FileScanner",
    "ScanMode",
    "FileScanner",
]

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from ...port.scanner import FileScan, ScanMode
from ...port.tree import ApiStyle, ScanModeG45
from ..path.guard import PathGuard
from ..tree._ast import AstOptions, AstTreeNode


def get_extractor(mode: ScanMode) -> FileScan:
    """Provide the right tool for the right task"""
    match mode:
        case ScanMode.READ:
            return raw_content_extractor
        case ScanMode.FST:
            return raw_content_extractor
        case ScanMode.AST:
            return raw_content_extractor


def raw_content_extractor(path: Path) -> str:
    """Default: Just read the file contents."""
    return path.read_text(encoding="utf-8")


@dataclass
class FileScanner:
    """
    Scan the selected files and extrac the desired content

    Use any FileExtractor starting from the simple Reader to
    more precise information extracted from Ast.

    """

    files: list[Path]
    local_root: Path
    mode: ScanMode = ScanMode.READ

    def split_paths(self) -> Iterator[tuple[Path, Path]]:
        """Create Pair of absolute and relative Path for all files"""
        for target in self.files:  # LATER: make this directly in PathGuard
            read_path, show_path = PathGuard.split(target, self.local_root)
            if not read_path.is_file():
                continue
            yield read_path, show_path

    def file_scan(self) -> Iterator[tuple[str, Path]]:
        """Scan all files by mode, skip fails and yield extracted results"""

        for read_path, show_path in self.split_paths():
            try:
                extractor: FileScan = get_extractor(self.mode)
                text: str = str(extractor(read_path))
            except (UnicodeDecodeError, OSError) as error:
                logger.debug(f"skip {read_path}: {error}")
                continue

            yield text, show_path


@dataclass
class G45FileScanner:
    files: list[Path]
    local_root: Path
    scan_mode: ScanModeG45 = ScanModeG45.RAW
    ast_options: AstOptions = field(default_factory=AstOptions)
    api_style: ApiStyle = ApiStyle.COMPACT

    def splitted_files(self):
        pass

    def file_scan(self) -> Iterator[tuple[str, Path]]:
        extractor = self._extractor()
        for read_path, show_path in self.splitted_files():
            try:
                text = extractor(read_path)
            except (UnicodeDecodeError, OSError) as error:
                logger.debug("skip {}: {}", read_path, error)
                continue
            if text is None:
                continue
            yield text, show_path

    def _extractor(self) -> FileExtractor:
        match self.scan_mode:
            case ScanModeG45.RAW:
                return raw_content_extractor
            case ScanModeG45.API:
                return AstExtractor(self.ast_options, self.api_style)

    def ast_forest(self) -> list[AstTreeNode]:
        """Optional: trees for TUI / multi-file overview."""
        ext = AstExtractor(self.ast_options, self.api_style)
        trees: list[AstTreeNode] = []
        for read_path, _show_path in self.splitted_files():
            if (t := ext.extract_tree(read_path)) is not None:
                # show_path.name as label if you prefer relative display
                trees.append(t)
        return trees


@dataclass
class AstScanner:
    """Folder walk + AST extract. CLI entry for --mode api / tree view."""

    folder: FolderScanner
    options: AstOptions = field(default_factory=AstOptions)
    style: ApiStyle = ApiStyle.COMPACT

    def files(self) -> list[Path]:
        return self.folder.get_files()

    def tree(self) -> AstTreeNode:
        ext = AstExtractor(self.options, self.style)
        branches = []
        for path in self.files():
            if path.suffix not in {".py", ".pyi"}:
                continue
            if (node := ext.extract_tree(path)) is not None:
                branches.append(node)
        return AstTreeNode(
            name=self.folder.scan_root.name,
            kind=AstKind.MODULE,
            branches=tuple(branches),
        )

    def summary_scanner(self) -> FileScanner:
        return FileScanner(
            files=self.files(),
            local_root=self.folder.scan_root,
            scan_mode=ScanMode.API,
            ast_options=self.options,
            api_style=self.style,
        )


# sketch — typer/argparse/click, whatever you use
def scan(
    root: Path,
    mode: ScanMode = ScanMode.RAW,
    api_style: ApiStyle = ApiStyle.COMPACT,
    public_only: bool = True,
    include_docs: bool = True,
    max_depth: int = 2,
    output: Path | None = None,
    show_tree: bool = False,
):
    folder = FolderScanner(root)
    options = AstOptions(
        public_only=public_only,
        include_docstrings=include_docs,
        max_depth=max_depth,
    )
    if show_tree and mode is ScanMode.API:
        _tree = AstScanner(folder, options, api_style).tree()
        # render_tui(tree)  # existing SimpleTreeNode UI
        return

    files = folder.get_files()
    _scanner = FileScanner(files, root, mode, options, api_style)
    # if output:
    #     SummaryFile.with_scanner(output, files, root, mode).write()
    # note: with_scanner must take options through — see below
