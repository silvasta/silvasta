"""
Provide Container for Files and Tools for FileSystem Operations

                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "FileQueryMixin",
]

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from ...port.files import File, FileQuery


class FileQueryMixin:
    """Provide basic registry access and confirmation"""

    # --- Mixin Dependencies (Expected from Host & SstFiles) ---
    root_dir: Path
    files: list[File]
    all: Iterable[File]
    # ----------------------------------------------------------

    def paths(self, resolve: bool = False) -> set[Path]:
        return set(
            file.path if not resolve else self.resolve(file)
            for file in self.all
        )

    def resolve(self, file: File) -> Path:
        return self.root_dir / file.path

    @property
    def has_duplicated_paths(self) -> bool:
        return len(self.paths()) < len(self.files)

    @property
    def has_duplicated_names(self) -> bool:
        return len(self.file_names) < len(self.files)

    @property
    def file_names(self) -> list[str]:
        return [file.name for file in self.files]

    def get_by_name(self, name: str) -> list[File]:
        return [file for file in self.files if file.name == name]

    def confirmed_files(self, local_dir: Path | None = None) -> list[File]:
        return self._check_file_status(local_dir, inverted=True)

    def unconfirmed_files(self, local_dir: Path | None = None) -> list[File]:
        return self._check_file_status(local_dir, inverted=False)

    def _check_file_status(
        self, local_dir: Path | None = None, inverted: bool = False
    ) -> list[File]:
        target_dir: Path = local_dir or self.root_dir
        return [
            file
            for file in self.all
            if bool(file.confirm_local_status(target_dir)) == inverted
        ]


if TYPE_CHECKING:
    _instance_check: FileQuery = FileQueryMixin()
    _class_check: type[FileQuery] = FileQueryMixin
