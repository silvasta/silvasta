"""
Implement the SstFile Tracker

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "SstFile",
]

import filecmp
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger
from pydantic import BaseModel, Field

from ...brick.view import Cli, Log, Rich, Str, view
from ...port.files import File


@view(cli=Cli.HEADER, str=Str.NAME, rich=Rich.MODULE, log=Log.DATA)
class SstFile(BaseModel):
    """Local file for upload and usage in prompt"""

    # NOTE: uuid? as option?
    path: Path  # relative from local filedir
    keywords: set = Field(default_factory=set)

    first_tracked: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    timestamp_format: str = "%Y-%m-%d_%H-%M-%S"

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def stem(self) -> str:
        return self.path.stem

    def touch(self) -> datetime:
        """Update last modification time"""
        self.last_updated: datetime = datetime.now(UTC)
        return self.last_updated

    @property
    def added_at(self) -> str:
        """Show creation time in local time zone"""
        return self.first_tracked.astimezone().strftime(self.timestamp_format)

    def confirm_local_status(self, root_dir: Path) -> bool:
        # NOTE: check local/global here? (absolute/relative)
        # - PathGuard has this already, check there first!
        file_path: Path = root_dir / self.path

        if not file_path.is_file():
            if not file_path.exists():
                msg: str = f"Nothing found at: {file_path=}"
            else:
                msg: str = f"No file found but exists: {file_path=}"
            logger.warning(msg)
            return False

        return True

    def _is_identical_to(self, other_path: Path, root_dir: Path) -> bool:
        """
        UNTESTED

        Fast structural comparison without reading full contents into memory
        """

        my_path = root_dir / self.path
        if not my_path.exists() or not other_path.exists():
            return False

        # Shallow=False forces content comparison if stat signatures match
        return filecmp.cmp(my_path, other_path, shallow=False)

    def _compute_hash(self, root_dir: Path, algorithm: str = "sha256") -> str:
        """
        UNTESTED

        Compute file hash via chunking (useful for databases/remotes)
        """
        my_path = root_dir / self.path
        if not my_path.is_file():
            return ""

        hasher = hashlib.new(algorithm)
        with my_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()


if TYPE_CHECKING:
    _instance_check: File = SstFile(path=Path())
    _class_check: type[File] = SstFile
