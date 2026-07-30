"""
Provide DTO for Summary File Content and Assembly

                                                       DependencyLevel[1]
"""

from typing import Self

__all__: list[str] = [
    "SummaryFile",
    "SummaryFileMachine",
]

from dataclasses import dataclass
from enum import StrEnum, auto
from functools import cached_property
from pathlib import Path

from loguru import logger

from ..path import PathGuard
from ..print import printer
from ..view import Cli, Str, view
from ._file import FileScanner, ScanMode


@view(cli=Cli.MARKDOWN, str=Str.NAME)
@dataclass
class SummaryFile:
    output_file: Path
    files: list[Path]
    local_root: Path
    scanner: FileScanner

    @classmethod
    def with_scanner(
        cls,
        output_file: Path,
        target_files: list[Path],
        local_root: Path,
        scan_mode: ScanMode,
    ) -> Self:
        """Increment output_file if needed and provide unique file"""
        scanner = FileScanner(target_files, local_root, scan_mode)
        return cls(output_file, target_files, local_root, scanner)

    @cached_property
    def text(self) -> str:
        parts: list[str] = self.compose()
        return "\n".join(parts)

    @property
    def n_lines(self) -> int:
        return len(self.text.splitlines())

    @property
    def name(self):
        return self.output_file.name

    @cached_property
    def machine(self) -> SummaryFileMachine:
        """Extract target file type from output file"""
        return SummaryFileMachine.from_path(self.output_file)

    @property
    @PathGuard.unique
    def unique_output_file(self) -> Path:
        """Increment output_file if needed and provide unique Path"""
        return self.output_file

    def write(self) -> str:
        # LATER: check for changes in target_files
        self.output_file.write_text(text := self.text)
        return text

    def compose(self) -> list[str]:
        """Send all target_files trough SummaryFileMachine and compose text"""
        return [
            self.machine.start(),
            *(
                scanned_text
                for content, show_path in self.scanner.file_scan()
                for scanned_text in self.machine.wrap(content, show_path)
                if scanned_text
            ),
            self.machine.final(),
        ]


class SummaryFileMachine(StrEnum):
    """Provide parts for Summary selection without missing any"""

    MD = auto()
    XML = auto()
    TXT = auto()

    def start(self) -> str:
        """First Line of Summary File"""
        match self:
            case SummaryFileMachine.MD:
                return "## Code Base"
            case SummaryFileMachine.XML:
                return "<codebase>"
            case SummaryFileMachine.TXT:
                return ""

    def wrap(self, content: str, path: Path) -> str:
        """Assemble Main Part with Content"""
        match self:
            case SummaryFileMachine.MD:
                return _wrap_for_md(path, content)
            case SummaryFileMachine.XML:
                return f'  <file path="{path}">\n{content}\n  </file>'
            case SummaryFileMachine.TXT:
                return f"--- file_path: {path} ---\n{content}"

    def final(self) -> str:
        """Last Line to close the Context"""
        match self:
            case SummaryFileMachine.MD | SummaryFileMachine.TXT:
                return ""
            case SummaryFileMachine.XML:
                return "</codebase>"

    @classmethod
    def from_path(cls, output_file: Path) -> SummaryFileMachine:
        """Match the Output file to the available types"""
        try:
            return cls(output_file.suffix.strip("."))
        except ValueError:
            printer.danger(["Unknown file type of output_file:", output_file])
            logger.warning(f"Unknown file type of output_file: {output_file}")
            return SummaryFileMachine.TXT


# ------------------------------------------------------------------ #
# Helper for Markdown content wrapper
# ------------------------------------------------------------------ #


def _wrap_for_md(path: Path, content: str) -> str:
    """Wrap file content in Markdown code blocks with appropriate comments."""

    language, comment = LANGUAGE_MAP.get(path.suffix, ("text", ""))
    close: str = "-->" if path.suffix in (".html", ".xml", ".md") else ""

    return _markdown_code_box(language, path, content, comment, close)


def _markdown_code_box(language, path, content, comment="", close=""):
    return f"""
```{language}
{comment} {path} {close}
{content}
```
"""


LANGUAGE_MAP: dict[str, tuple[str, str]] = {
    ".py": ("python", "#"),
    ".pyi": ("python", "#"),
    ".rs": ("rust", "//"),
    ".toml": ("toml", "#"),
    ".tex": ("tex", "%"),
    ".cls": ("tex", "%"),
    ".lua": ("lua", "--"),
    # Highly recommended additions!
    ".js": ("javascript", "//"),
    ".ts": ("typescript", "//"),
    ".json": ("json", "//"),
    ".yml": ("yaml", "#"),
    ".yaml": ("yaml", "#"),
    ".sh": ("bash", "#"),
    ".bash": ("bash", "#"),
    ".cpp": ("cpp", "//"),
    ".c": ("c", "//"),
    ".go": ("go", "//"),
    ".html": ("html", "<!--"),
    ".xml": ("xml", "<!--"),
    ".md": ("markdown", "<!--"),
}
