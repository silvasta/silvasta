from collections.abc import Iterator
from contextlib import suppress
from dataclasses import dataclass, field
from enum import StrEnum, auto
from pathlib import Path

from loguru import logger

from .filter import FilterSet, PathFilter, ProjectFilter
from .pathguard import PathGuard
from .print import printer
from .simple_tree import PathTreeNode, build_path_tree


class TargetFileType(StrEnum):
    MD = auto()
    XML = auto()
    TXT = auto()

    def start_part(self) -> str:
        return {
            TargetFileType.MD: "# Code Base",
            TargetFileType.XML: "<codebase>",
            TargetFileType.TXT: "",
        }[self]

    def content(self, rel_path: Path, content: str) -> str:
        match self:
            case TargetFileType.MD:
                return self.format_for_md(rel_path, content)
            case TargetFileType.XML:
                return f'  <file path="{rel_path}">\n{content}\n  </file>'
            case TargetFileType.TXT:
                return f"--- file_path: {rel_path} ---\n{content}"

    def end_part(self) -> str:
        return {
            TargetFileType.MD: "",
            TargetFileType.XML: "</codebase>",
            TargetFileType.TXT: "",
        }[self]

    @staticmethod
    def format_for_md(path: Path, content: str) -> str:
        match path.suffix:
            case ".py":
                return f"```python\n# {path}\n{content}\n```"
            case ".rs":
                return f"```rust\n// {path}\n{content}\n```"
            case _:
                return f"{path}\n```\n{content}\n```"


@dataclass
class FolderScanner:
    """Scan downwards from local root, filter, get path list or load files"""

    scan_root: Path

    path_filter: PathFilter[str | Path] = field(default_factory=ProjectFilter)

    # Used to create local summary file
    output_dir: Path = field(default_factory=Path.cwd)
    output_stem: str = "summary"

    _debug: bool = False

    def scan_local_files(self, get_absolute_paths: bool = False) -> list[Path]:
        """Get list of absolute paths of local files that match predefined conditions"""
        return [
            path
            if get_absolute_paths
            else PathGuard.relative(target=path, root=self.scan_root)
            for path in self.walk(
                self.scan_root, self.path_filter, debug=self._debug
            )
        ]

    @classmethod
    def walk(
        cls, root: Path, path_filter: FilterSet | None = None, debug=False
    ) -> Iterator[Path]:
        """Walk directory downwards and yield absolute file paths that match filter"""
        path_filter: FilterSet = path_filter or ProjectFilter()

        for item in root.iterdir():
            if not path_filter(item):
                if debug:
                    logger.debug(f"ignoring: {item=}")

                continue

            if item.is_dir():
                if debug:
                    logger.debug(f"yield from folder: {item=}")

                yield from cls.walk(item, path_filter)

            if item.is_file():
                if debug:
                    logger.debug(f"yield file: {item=}")

                yield item

    def filesystem_tree(self) -> PathTreeNode:
        return build_path_tree(
            paths=self.scan_local_files(), root_name=self.scan_root.name
        )

    @classmethod
    def tree(
        cls, root: Path, path_filter: FilterSet | None = None
    ) -> PathTreeNode:
        return build_path_tree(
            paths=list(cls.walk(root=root, path_filter=path_filter)),
            root_name=root.name,
        )

    # IMPORTANT: make easy function with input: list[Path]
    # - recognize target from output_file
    # - as much as possible in 1 step

    @staticmethod
    def assemble_summary_file(
        paths: list[Path],
        target: TargetFileType,
        scan_root: Path | None = None,
    ) -> str:

        parts: list[str] = [target.start_part()]

        for path_pair in PathGuard.split_read_print_path(paths, scan_root):
            read_path, print_path = path_pair

            if read_path.is_dir():
                logger.debug(f"ignoring dir: {print_path}")
                continue

            with suppress(UnicodeDecodeError):
                content: str = read_path.read_text(encoding="utf-8")
                parts.append(target.content(print_path, content))

        parts += [target.end_part()]

        return "\n\n".join(parts) if parts else "\n\n"

    def create_summary_file(
        self,
        target: TargetFileType,
        output_file: Path | None = None,
    ):
        output_file = output_file or self._name_from_target(target)

        files: list[Path] = self.scan_local_files()

        printer.lines_from_list(
            header="Files for Summary",
            title="FolderScanner",
            lines=[str(path) for path in files],
            style="yellow",
        )

        data: str = FolderScanner.assemble_summary_file(
            files, target, scan_root=self.scan_root
        )

        PathGuard.unique(output_file).write_text(data)

    @classmethod
    def _name_from_target(cls, target) -> Path:
        return cls.output_dir / f"{cls.output_stem}.{target.value}"

    @classmethod
    def target_from_path(cls, output_file: Path) -> TargetFileType:
        # MERGE: into create/assemble file
        return TargetFileType(output_file.suffix.strip("."))

    def write_summary_with_name(self, filename: str):
        output_file: Path = self.output_dir / filename
        self.write_summary_with_path(output_file)

    def write_summary_with_path(self, output_path: Path):
        try:
            suffix: str = output_path.suffix.strip(".")
            target: str = TargetFileType(value=suffix)
        except ValueError:
            logger.error(f"Unable to identify target for: {output_path=}")
            raise

        self.create_summary_file(target, output_path)
