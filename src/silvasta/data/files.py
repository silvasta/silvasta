from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr

from silvasta.config import ConfigManager, get_config

from ..utils import FilterSet, FolderScanner, PathGuard, ProjectFilter


class SstFile(BaseModel):
    """Local file for upload and usage in prompt"""

    # IDEA: original name at load
    # - then slugify?
    # - possible to get name changes due to duplicated names but from different files
    # -> test first in sachmis

    local_path: Path  # relative from local filedir # NOTE: confirm?
    keywords: set = Field(default_factory=set)

    first_tracked: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))

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


class FileRegistry[FilesT: SstFile](BaseModel):
    """Registry for Local Files"""

    local_root: Path
    _scanner: FolderScanner | None = PrivateAttr(default=None)

    files: list[FilesT] = Field(default_factory=list)  # IDEA: any iterable?

    file_factory: Callable[..., FilesT] = Field(exclude=True)

    def _attach(self, file: FilesT):
        self.files.append(file)

    def _create_local_file(self, path: Path) -> FilesT:
        if path.is_absolute():
            path: Path = self.relative_to_local_root(path)
        logger.debug(f"create new file: {path=}")
        return self.file_factory(local_path=path)

    def attach_from_path(self, path) -> FilesT:
        file: FilesT = self._create_local_file(path)
        self._attach(file)
        return file

    def relative_to_local_root(self, path: Path, strict: bool = True) -> Path:
        """Get path if inside local root, strict=False tries: ../../file.txt"""
        relative_path: Path = PathGuard.relative(
            target=path, root=self.local_root, strict=strict
        )
        logger.debug(f"Created {relative_path=} from:\n{path=}")
        return relative_path

    def attach_new_files_from_local_folder(self) -> list[FilesT]:
        """Load files to registry that are not already attached"""

        new_files: list[FilesT] = []
        existing: set[Path] = self.local_file_paths

        for path in self.scan_local_dir():
            if path not in existing:
                new_file: FilesT = self.attach_from_path(path)
                new_files.append(new_file)

        return new_files

    def update_files_from_local_folder(self) -> None:
        """Load new files and update files in registry if they changed"""
        raise NotImplementedError  # LATER: changed? date? keywords? hash?

    def reload_all_files_from_local_folder(self):
        """Load files to registry and remove files with same path"""

        new_files: list[FilesT] = []

        for path in self.scan_local_dir():
            for file in self.get_files_by_path(path):
                logger.debug(f"removing: {file}")
                self.files.remove(file)

            new_file: FilesT = self.attach_from_path(path)
            new_files.append(new_file)

        return new_files

    def scan_local_dir(self) -> list[Path]:
        scanner: FolderScanner = self.get_scanner()
        return scanner.scan_local_files(get_absolute_paths=False)

    def get_scanner(self) -> FolderScanner:
        if not self._scanner:
            return self.setup_scanner(path_filter=ProjectFilter())
        return self._scanner

    def setup_scanner(self, path_filter: FilterSet) -> FolderScanner:
        self._scanner = FolderScanner(self.local_root, path_filter=path_filter)
        return self._scanner

    @property
    def local_file_paths(self) -> set[Path]:
        return set(file.local_path for file in self.files)

    @property
    def has_duplicated_file_paths(self) -> bool:
        return len(self.local_file_paths) < len(self.files)

    @property
    def global_file_paths(self) -> set[Path]:
        # TODO: naming to absolute_...?
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

    def get_files_by_filter(self, file_filter: SstFileFilter) -> list[FilesT]:
        """Get all files filtered by keywords setup in file_filter"""
        return [file for file in self.files if file_filter(file)]

    def get_files_by_keyword(self, keywords: str | list[str]) -> list[FilesT]:
        """Get all files that have at least 1 of the required keywords"""
        if isinstance(keywords, str):
            keywords: list[str] = [keywords]

        keyword_filter: SstFileFilter = SstFileFilter(
            require_any=set(keywords)
        )
        return [file for file in self.files if keyword_filter(file)]

    def get_files_with_all_keywords(self, keywords: list[str]) -> list[FilesT]:
        """Get all files that have all of the required keywords"""

        keyword_filter: SstFileFilter = SstFileFilter(
            require_all=set(keywords)
        )
        return [file for file in self.files if keyword_filter(file)]


class FileSystemManager:
    """Manager for operations on Local Files"""

    # LATER: define what can be added to general lib
