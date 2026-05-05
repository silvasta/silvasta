from collections.abc import Callable
from datetime import UTC, datetime
from functools import singledispatchmethod
from pathlib import Path
from typing import Any, Self

from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr

from sstcore.utils.simple_tree import build_path_tree

from ..config import ConfigManager, get_config
from ..exceptions import NotImplementedDispatchError, RegistrySyncError
from ..utils import (
    FilterSet,
    FolderScanner,
    PathFilter,
    PathGuard,
    PathTreeNode,
    ProjectFilter,
)


class SstFile(BaseModel):
    """Local file for upload and usage in prompt"""

    local_path: Path  # relative from local filedir
    keywords: set = Field(default_factory=set)

    first_tracked: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_temp_file(self) -> bool:  # LATER: check if needed
        return self.local_path == Path()

    @property
    def description(self) -> str:
        """Extensive description formatted with Rich Color String"""
        config: ConfigManager = get_config()
        return config.names.sstfile_dates.styled(self._description)

    @property
    def _description(self) -> list[str | datetime | Path]:
        """Constructor for (raw) description text blocks"""
        return [self.name, self.first_tracked, self.last_updated]

    @property
    def raw_description(self) -> str:
        """Raw description without any coloring"""
        config: ConfigManager = get_config()
        return config.names.sstfile_dates(self._description)

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
    """Local Registry with Files relative to Root, provides
    basic operations to handle files and groups of files"""

    local_root: Path
    _scanner: FolderScanner | None = PrivateAttr(default=None)

    files: list[FilesT] = Field(default_factory=list)  # IDEA: any iterable?

    @property
    def n_files(self):
        return len(self.files)

    @property
    def local_file_paths(self) -> set[Path]:
        return set(file.local_path for file in self.files)

    @property
    def has_duplicated_file_paths(self) -> bool:
        return len(self.local_file_paths) < len(self.files)

    # TODO: here or in SstFile? (same for confirm_local_status)
    # - maybe both in both directions? arg: path <-> File
    # def has_incremented_file_paths(self):

    @property
    def absolute_file_paths(self) -> set[Path]:
        return set(self.local_root / file.local_path for file in self.files)

    @property
    def file_names(self) -> set[str]:
        return set(file.name for file in self.files)

    @property
    def has_duplicated_file_names(self) -> bool:
        return len(self.file_names) < self.n_files

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

    def get_files_by_path(self, path: Path) -> list[FilesT]:
        # LATER: get_file_by_path  that handles case 0,1,_ already here? (only -> FilesT)
        local_path: Path = self.relative_to_local_root(path)
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

    def relative_to_local_root(self, path: Path, strict: bool = True) -> Path:
        """Create relative path from local_root, just forward already relative,
        strict=False tries to create paths like: ../../file.txt"""

        if not path.is_absolute():
            logger.debug(f"Forwarding relative {path=} for {self.local_root=}")
            return path

        relative_path: Path = PathGuard.relative(
            target=path, root=self.local_root, strict=strict
        )

        logger.debug(f"Created {relative_path=} from: {path=}")
        return relative_path

    def ensure_local_path(self, path: Path) -> Path:
        """Transform and confirm absolute path into relative, confirm relative path"""
        if path.is_absolute():
            try:
                return self.relative_to_local_root(path, strict=True)
            except ValueError:
                spec = "Absolute"
        else:
            try:
                return PathGuard.file(target=self.local_root / path)
            except FileNotFoundError:
                spec = "Relative"

        raise RegistrySyncError(
            f" Invalid {spec} {path=}! Not inside {self.local_root=}!"
        )

    def create_local_file(self, path: Path) -> FilesT:
        """Ensure file is inside local_root, create instance with abstract constructor"""
        local_path: Path = self.ensure_local_path(path)
        file: FilesT = self._create_local_file(local_path)
        logger.debug(f"New file created: {file.local_path=}")
        return file

    def _create_local_file(self, *_args, **_kwargs) -> FilesT:
        """Derive class and override this to set file constructor"""
        msg = f"{self.__class__.__name__} has no implementation of _create_local_file!"
        raise NotImplementedError(msg)

    def attach(self, file: FilesT, strict=True):
        """Check if File is valid local file and attach to Registry"""

        if not file.confirm_local_status(self.local_root):
            logger.error(f"Cannot attach file: {file.raw_description}")
            if not strict:
                logger.warning(f"Ignoring: {file.raw_description}")
            else:
                raise RegistrySyncError("File missing on local disk")

        self._attach(file)

    def _attach(self, file: FilesT):
        """Override _attach to handle other types than list[FilesT]"""
        self.files.append(file)

    def attach_from_path(self, path) -> FilesT:
        """Attach File that is already inside local_root"""
        file: FilesT = self.create_local_file(path)
        self.attach(file)
        return file

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

    def reload_all_files_from_local_folder(self, *, clear_all=False):
        """Load all files inside local_root to registry,
        Override existing registry Files, clear_all: start from empty status"""

        if clear_all:
            logger.info(f"Removing {self.n_files} files...")
            self.files.clear()

        new_files: list[FilesT] = []

        for path in self.scan_local_dir():
            new_file: FilesT = self.attach_from_path(path)

            if not clear_all:
                for file in self.get_files_by_path(path):
                    logger.debug(f"removing: {file}")
                    self.files.remove(file)

            new_files.append(new_file)

        return new_files

    def clone_empty_registry(
        self,
        local_root,
        exclude: set[str] | None = None,
        add_to_exclude: set[str] | None = None,
        exclude_unset=False,
    ) -> Self:
        """Get registry with same configuration, new local_root and No files"""
        if exclude is None:
            exclude: set[str] = {"files", "local_root"}
        if add_to_exclude:
            exclude: set[str] = exclude | add_to_exclude
        cloned_data: dict[str, Any] = self.model_dump(
            exclude=exclude, exclude_unset=exclude_unset, mode="python"
        )
        return type(self)(local_root=local_root, **cloned_data)

    def mirror_from_path(self, source: Path | list[Path]) -> list[FilesT]:
        """Copy external files from into local_root and add to registry"""
        return self._sync_external_files(
            source, transfer_strategy=PathGuard.copy
        )

    def absorb_from_path(self, source: Path | list[Path]) -> list[FilesT]:
        """Move external files from into local_root and add to registry"""
        return self._sync_external_files(
            source, transfer_strategy=PathGuard.rotate
        )

    def mirror_from_registry(self, external_registry: Self) -> list[FilesT]:
        """Copy files of external registry into local_root and add to registry"""
        return self._sync_registry(
            external_registry, transfer_strategy=PathGuard.copy
        )

    def absorb_from_registry(self, external_registry: Self) -> list[FilesT]:
        """Move files of external registry into local_root and add to registry"""
        return self._sync_registry(
            external_registry, transfer_strategy=PathGuard.rotate
        )

    @singledispatchmethod
    def _sync_external_files(
        self,
        source: Path | list[Path],
        transfer_strategy: Callable[[Path, Path], Path],
    ) -> list[FilesT]:
        """Mirror or Absorb external file source, dispatch file or dir"""
        raise NotImplementedDispatchError(source, transfer_strategy)

    @_sync_external_files.register
    def _(
        self, source: list, transfer_strategy: Callable[[Path, Path], Path]
    ) -> list[FilesT]:
        """Concat multiple file sources"""
        return [
            file
            for path in source
            for file in self._sync_external_files(
                source=path, transfer_strategy=transfer_strategy
            )
        ]

    @_sync_external_files.register
    def _(
        self, source: Path, transfer_strategy: Callable[[Path, Path], Path]
    ) -> list[FilesT]:
        """Mirror or Absorb external file source, dispatch file or dir"""

        if source.is_dir():
            temp_registry: Self = self.clone_empty_registry(local_root=source)
            temp_registry.attach_new_files_from_local_folder()
            return self._sync_registry(
                external_registry=temp_registry,
                transfer_strategy=transfer_strategy,
            )
        if source.is_file():
            return [
                self._fetch_external_file(
                    source, transfer_strategy=transfer_strategy
                )
            ]

        action: str = getattr(transfer_strategy, "__name__", "Task")
        logger.error(f"Nothing to do for {action}! Invalid path: {source=}")
        return []

    def _sync_registry(
        self,
        external_registry: Self,
        transfer_strategy: Callable[[Path, Path], Path],
    ) -> list[FilesT]:
        """Attach data from external registry"""
        new_files: list[FilesT] = []

        for file in external_registry.files:
            source: Path = external_registry.local_root / file.local_path

            file: FilesT = self._fetch_external_file(
                source,
                new_local_path=file.local_path,
                transfer_strategy=transfer_strategy,
            )
            self.attach(file)
            new_files.append(file)

        return new_files

    def _fetch_external_file(
        self,
        source: Path,
        transfer_strategy: Callable[[Path, Path], Path],
        new_local_path: Path | str | None = None,
    ) -> FilesT:
        """Copy or Move file into local_root and load new File into registry"""
        # LATER: flag for:
        # - ignore if target exists
        # - override target
        # now is just create new file with incremented unique of target
        # - maybe do this inside transfer_strategy?
        new_local_path: Path | str = new_local_path or source.name  # PARAM:

        target: Path = self.local_root / new_local_path
        unique_target: Path = transfer_strategy(source, target)

        if target != unique_target:
            logger.warning(f"Incremented source to {unique_target.name=}")

        file: FilesT = self.attach_from_path(path=unique_target)

        action: str = getattr(transfer_strategy, "__name__", "Task")
        logger.debug(f"{action} completed: {file.description}")

        return file

    def scan_local_dir(self) -> list[Path]:
        scanner: FolderScanner = self.get_scanner()
        return scanner.scan_local_files(get_absolute_paths=False)

    def get_scanner(self) -> FolderScanner:
        if not self._scanner:
            return self.setup_scanner(path_filter=ProjectFilter())
        return self._scanner

    def setup_scanner(self, path_filter: PathFilter) -> FolderScanner:
        self._scanner = FolderScanner(self.local_root, path_filter=path_filter)
        return self._scanner

    def tree(
        self,  # LATER: create SstFileTree?
        root_name: str | None = None,
        file_filter: SstFileFilter | None = None,
    ) -> PathTreeNode:
        if root_name is None:
            root_name: str = self.local_root.name
        files: list[Path] = (
            [file.local_path for file in self.get_files_by_filter(file_filter)]
            if file_filter
            else list(self.local_file_paths)
        )
        return build_path_tree(
            paths=files,
            root_name=root_name,
        )


class SstFileRegistry(FileRegistry[SstFile]):
    """Registry with SstFile as constructor for new files"""

    def _create_local_file(self, path: Path) -> SstFile:
        return SstFile(local_path=path)


class FileSystemManager:
    """Manager for operations on Local Files"""
