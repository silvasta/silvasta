"""
Provide Container for Files and Tools for FileSystem Operations

                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "FileQueryRegistry",
]

from collections.abc import Iterable
from pathlib import Path

from ...port.files import File, QueryRegister
from ...port.link import portlink


@portlink(QueryRegister)
class FileQueryRegistry:
    """Provide basic registry access and confirmation"""

    root_dir: Path
    files: list[File]
    all: Iterable[File]

    def paths(self, resolve: bool = False) -> set[Path]:
        return set(
            file.path if not resolve else self.resolve(file)
            for file in self.all  # TODO: in self: __iter__
        )

    def resolve(self, file: File) -> Path:
        return self.root_dir / file.path

    @property
    def has_duplicated_paths(self) -> bool:
        return len(self.paths()) < len(self.files)

    @property
    def has_duplicated_names(self) -> bool:
        return len(self.names) < len(self.files)

    @property
    def names(self) -> list[str]:
        return [file.name for file in self.files]

    def by_name(self, name: str) -> list[File]:
        # NEXT: make this Registry.find
        return [file for file in self.files if file.name == name]

    def confirmed(self, local_dir: Path | None = None) -> list[File]:
        return self._check_file_status(local_dir, inverted=True)

    def unconfirmed(self, local_dir: Path | None = None) -> list[File]:
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
