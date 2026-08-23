"""
Provide Container for Files and Tools for FileSystem Operations

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "SstFiles",
]

from pathlib import Path
from typing import TYPE_CHECKING

from ...brick.registry import ListRegistry
from ...error import PathGuardError, RegistrySyncError
from ...port.files import File, Files
from ...util import PathGuard


class SstFiles(ListRegistry):
    """Provide basic registry access and confirmation"""

    root_dir: Path

    @property
    def files(self) -> list[File]:
        return self.items

    @files.setter
    def files(self, value: list[File]) -> None:
        self.items: list[File] = value

    def _item_identifier(self, item: File) -> Path:
        """Plug ListRegistry identity into SstFile.path"""

        return item.path

    def ensure_path(self, path: Path) -> Path:
        """Confirm path exists inside root_dir and return its relative path."""
        target: Path = path if path.is_absolute() else self.root_dir / path
        try:
            return self.relative_to_root(target, strict=True)
        except (ValueError, PathGuardError) as error:
            raise RegistrySyncError(
                f"Invalid {path=}! Not inside {self.root_dir}!"
            ) from error

    def relative_to_root(self, path: Path, strict: bool = True) -> Path:
        if not path.is_absolute():
            return path
        return PathGuard.relative(path, self.root_dir, strict=strict)

    def attach_from_path(self, path: Path, strict: bool = True) -> File:
        """Attach File that is already inside root_dir"""
        file: File = self.create_local_file(path, strict=strict)
        self.attach(file)
        return file

    def create_local_file(self, path: Path, *, strict=True) -> File:
        """Ensure path is valid and create File with subhook constructor"""
        path: Path = self.ensure_path(path)
        file: File = self._create_local_file(path)
        if not file.confirm_local_status(self.root_dir) and strict:
            raise RegistrySyncError("File Missing on Disk!", file=file)
        return file

    def _create_local_file(self, *_args, **_kwargs) -> File:
        """Derive class and override this to set file constructor"""
        raise NotImplementedError(f"Create File from: {self}")


if TYPE_CHECKING:
    _instance_check: Files = SstFiles()
    _class_check: type[Files] = SstFiles
