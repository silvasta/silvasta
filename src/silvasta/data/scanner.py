from collections.abc import Iterator
from enum import StrEnum, auto
from pathlib import Path

from loguru import logger

from silvasta.config import ConfigManager, get_config
from silvasta.utils import PathGuard

# MOVE: path.utils?

# TASK: scan config / settings
# - once for projects, Python/Rust
# - once for university
# - some other?

PROJECT_IGNORE_DIRS: set[str] = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "target",
}

PROJECT_ALLOWED_EXTS: set[str] = {
    ".py",
    ".rs",
    ".md",
    ".json",
    ".yaml",
    ".toml",
}

# TASK: this with walkdir, load paths, select with SimpleTree in TUI

# TASK: make this files hold and later on compare, like git


def format_for_md(path: Path, content: str):
    match path.suffix:
        case ".py":
            f"```python\n# {path}\n{content}\n```"
        case ".rs":
            f"```rust\n// {path}\n{content}\n```"
        case _:
            f"{path}\n```\n{content}\n```"


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


class FolderScanner:
    # TODO: check if class actually needed,
    # check with PathGuard
    # check if files could/should be hold here
    # check how can be used as cls but still with some init to save unimportant atributes for comfort

    # NOTE: important attributes: black/white list!!!

    def __init__(
        self,
        scan_root: Path | None = None,
        output_dir: Path | None = None,
        output_stem: str = "",
    ):
        config: ConfigManager = get_config()
        self.scan_root: Path = scan_root or config.paths.project_root

        self.output_dir: Path = output_dir or Path.cwd()
        self.output_stem: str = output_stem or "summary"

    @staticmethod
    def walk_directory(
        root_path: Path, folder_blacklist: set[str], ext_whitelist: set[str]
    ) -> Iterator[Path]:
        """Yield files downwards from folder, filter with black/white-list"""

        for item in root_path.iterdir():
            if item.is_dir():
                if item.name not in folder_blacklist:
                    yield from FolderScanner.walk_directory(
                        item, folder_blacklist, ext_whitelist
                    )
            elif item.is_file():
                if item.suffix in ext_whitelist:
                    yield item

    def write_to_local_root(
        self,
        files: list[Path],
        target: TargetFileType | None,
        filename: str | None = None,
    ):
        output_name: str = filename or f"{self.output_stem}.{target}"
        output_file: Path = self.output_dir / output_name

        if not target:
            self.write_to_path(files, output_file)
        else:
            self.write(files, target, output_file)

    def write(
        self,
        files: list[Path],
        target: TargetFileType,
        output_file: Path,
    ):
        data: str = self.create_file(files, target)

        PathGuard.unique(output_file).write_text(data)

    def write_to_path(
        self,
        files: list[Path],
        path: Path,
    ):
        try:
            target: str = TargetFileType(path.suffix.strip("."))
        except ValueError:
            logger.error(f"Unable to identify target for: {path=}")
            raise

        self.write(files, target, path)

    def create_file(self, paths: list[Path], target: TargetFileType) -> str:
        parts: list[str] = [target.start_part()]

        for path in paths:
            try:
                content: str = path.read_text(encoding="utf-8")
                rel_path: Path = path.relative_to(self.scan_root)
                parts.append(target.content(rel_path, content))
            except UnicodeDecodeError:
                pass  # Skip accidental binary files

        parts += [target.end_part()]

        return "\n\n".join(parts)
