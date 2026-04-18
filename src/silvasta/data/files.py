from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import ParamSpec

from loguru import logger
from pydantic import BaseModel, Field

from ..utils import PathGuard
from ..utils.filter import FilterSet
from ..utils.scanner import FolderScanner


class SstFile(BaseModel):
    """Local file for upload and usage in prompt"""

    local_path: Path  # relative from local filedir # NOTE: confirm?
    # IDEA: original name at load
    # - then slugify?
    # - possible to get name changes due to duplicated names but from different files
    # -> test first in sachmis
    keywords: set = Field(default_factory=set)

    # TODO: timezone
    first_tracked: datetime = Field(default_factory=datetime.now(UTC))
    last_updated: datetime = Field(default_factory=datetime.now(UTC))

    @property
    def is_temp_file(self) -> bool:
        return self.local_path == Path()  # TODO: check if needed

    @property
    def name(self) -> str:
        return self.local_path.name

    @property
    def stem(self) -> str:
        return self.local_path.stem

    def touch(self) -> datetime:
        self.last_updated: datetime = datetime.now(UTC)
        return self.last_updated

    def confirm_local_status(self, local_dir: Path) -> bool:
        file_path: Path = local_dir / self.local_path
        if not file_path.is_file():
            if not file_path.exists():
                msg: str = f"Nothing found at: {file_path=}"
            else:
                msg: str = f"No file found but exists: {file_path=}"
            logger.warning(msg)
            return False
        return True

    # LATER: check for changes, hash, etc


class SstFileFilter[SetType: str, ObjectType: SstFile](FilterSet):
    def _create_target_set(self, target: SstFile) -> set[str]:
        return target.keywords


semester_filter = SstFileFilter(
    exclude=set(["exam"]),
    require_any=set(["lecture", "exercise"]),
)

file = SstFile(local_path=Path("mpc/lecture_4.pdf"))

print(semester_filter(file))


class FileRegistry[FilesT: SstFile](BaseModel):
    """Registry for Local Files"""

    file_constructor: Callable[ParamSpec[Path], FilesT]  # NOTE: unsure

    local_root: Path

    files: list[FilesT] = Field(default_factory=list)  # IDEA: any iterable?

    def relative_to_local_root(self, path: Path) -> Path:
        return PathGuard.compute_relative(target=path, root=self.local_root)

    def attach_from_path(self, path) -> FilesT:
        local_path: Path = self.relative_to_local_root(path)
        logger.debug(f"attach new file: {local_path=}")
        file: FilesT = self._create_local_file(local_path)
        self._attach(file)
        return file

    def _attach(self, file: FilesT):
        self.files.append(file)

    def _create_local_file(self, path: Path) -> FilesT:
        return self.file_constructor(  # NOTE: unsure if creation here
            local_path=self.relative_to_local_root(path)
        )

    @property
    def local_file_paths(self) -> set[Path]:
        return set(file.local_path for file in self.files)

    @property
    def has_duplicated_file_paths(self) -> bool:
        return len(self.local_file_paths) < len(self.files)

    @property
    def global_file_paths(self) -> set[Path]:
        return set(self.local_root / file.local_path for file in self.files)

    @property
    def file_names(self) -> set[str]:
        return set(file.name for file in self.files)

    @property
    def has_duplicated_file_names(self) -> bool:
        return len(self.file_names) < len(self.files)

    def get_confirmed_files(
        self, local_dir: Path | None = None
    ) -> list[FilesT]:
        local_dir: Path = local_dir or self.local_root

        return [
            file  # all files with valid path
            for file in self.files
            if file.confirm_local_status(local_dir)
        ]

    def get_not_confirmed_files(
        self, local_dir: Path | None = None
    ) -> list[FilesT]:
        local_dir: Path = local_dir or self.local_root

        return [
            file  # all files without valid path
            for file in self.files
            if not file.confirm_local_status(local_dir)
        ]

    def get_files_by_path(self, local_path: Path) -> list[FilesT]:
        return [file for file in self.files if file.local_path == local_path]

    def get_files_by_name(self, name: str) -> list[FilesT]:
        return [file for file in self.files if file.name == name]

    def attach_new_files_from_local_folder(self) -> list[FilesT]:
        """Load files to registry that are not already attached"""

        new_files: list[FilesT] = []
        local_file_paths: set[Path] = self.local_file_paths

        for path in self._scan_local_dir():
            local_path: Path = self.relative_to_local_root(path)

            if local_path in local_file_paths:
                logger.debug(f"skipping {path=}")  # REMOVE: after tests
            else:
                new_file: FilesT = self.attach_from_path(path)
                new_files.append(new_file)

        return new_files

    def update_files_from_local_folder(self) -> None:
        """Load new files and update files in registry if they changed"""
        raise NotImplementedError  # LATER: changed? date? keywords? hash?

    def reload_all_files_from_local_folder(self):
        """Load files to registry and remove files with same path"""

        new_files: list[FilesT] = []

        for path in self._scan_local_dir():
            local_path: Path = self.relative_to_local_root(path)

            for file in self.get_files_by_path(local_path):
                logger.debug(f"removing: {file}")
                self.files.remove(file)

            new_file: FilesT = self.attach_from_path(path)
            new_files.append(new_file)

        return new_files

    def _scan_local_dir(self) -> list[Path]:
        return FolderScanner.scan_local_files(self.local_root)


class FileSystemManager:
    """Manager for operations on Local Files"""
