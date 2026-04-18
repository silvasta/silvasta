from enum import StrEnum, auto
from pathlib import Path

from loguru import logger

from silvasta.utils import PathGuard
from silvasta.utils.path import PathFilter, find_project_root, walk_directory


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
                return format_for_md(rel_path, content)
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


def format_for_md(path: Path, content: str) -> str:
    match path.suffix:
        case ".py":
            return f"```python\n# {path}\n{content}\n```"
        case ".rs":
            return f"```rust\n// {path}\n{content}\n```"
        case _:
            return f"{path}\n```\n{content}\n```"


# MOVE: to config.defaults or new class
PROJECT_IGNORE_DIRS: set[str] = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "target",
}

# MOVE: to config.defaults or new class
PROJECT_ALLOWED_EXTS: set[str] = {
    # TODO: check for opposite forbidden(folder fail otherwise)
    ".py",
    ".rs",
    ".md",
    ".json",
    ".yaml",
    ".toml",
}


class FolderScanner:
    path_filter: PathFilter = PathFilter(
        exclude=PROJECT_IGNORE_DIRS,
        require_any=PROJECT_ALLOWED_EXTS,  # TODO: check for opposite forbidden(folder fail otherwise)
    )
    output_dir: Path = Path.cwd()
    output_stem: str = "summary"

    def __init__(
        self,
        scan_root: Path,
        path_filter: PathFilter | None = None,
        output_dir: Path | None = None,
        output_stem: str | None = None,
    ):
        self.scan_root: Path = scan_root

        if path_filter is not None:
            self.path_filter: PathFilter = path_filter

        if output_dir:
            self.output_dir: Path = output_dir or Path.cwd()
        if output_stem:
            self.output_stem: str = output_stem or "summary"

    def scan_local_files(self, scan_root: Path) -> list[Path]:
        return list(walk_directory(scan_root, self.path_filter))

    @staticmethod
    def assemble_summary_file(
        paths: list[Path],
        target: TargetFileType,
        scan_root: Path | None = None,
    ) -> str:
        parts: list[str] = [target.start_part()]

        for path in paths:
            try:
                content: str = path.read_text(encoding="utf-8")
                if scan_root and (
                    relative_path := PathGuard.find_relative(path, scan_root)
                ):
                    path: Path = relative_path
                parts.append(target.content(path, content))
            except UnicodeDecodeError:
                pass  # Skip accidental binary files

        parts += [target.end_part()]
        return "\n\n".join(parts) if parts else "\n\n"

    def create_summary_file(
        self,
        target: TargetFileType,
        output_file: Path | None = None,
    ):
        output_file = output_file or FolderScanner._name_from_target(target)

        files: list[Path] = self.scan_local_files(self.scan_root)
        data: str = FolderScanner.assemble_summary_file(files, target)

        PathGuard.unique(output_file).write_text(data)

    @classmethod
    def _name_from_target(cls, target) -> Path:
        return cls.output_dir / f"{cls.output_stem}.{target}"

    def write_summary_with_name(self, filename: str):
        output_file: Path = self.output_dir / filename
        self.write_summary_with_path(output_file)

    def write_summary_with_path(self, output_path: Path):
        try:
            target: str = TargetFileType(output_path.suffix.strip("."))
        except ValueError:
            logger.error(f"Unable to identify target for: {output_path=}")
            raise

        self.create_summary_file(target, output_path)


if __name__ == "__main__":
    scanner: FolderScanner = FolderScanner(
        scan_root=find_project_root() / "src/silvasta",
        path_filter=PathFilter(
            exclude=PROJECT_IGNORE_DIRS,
            require_any={
                "path",
                "scanner",
                "filter",
                "files",
            },
        ),
    )
    scanner.write_summary_with_name("summary.md")
