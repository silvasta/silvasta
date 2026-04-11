from datetime import datetime
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field

# LATER:
# - first_invalid / last valid
# - updated as list of updates:
#   - last_updated as property
#   - to heavy? force len(update_list) ~ 1
#   - still to much computation for nothing? check!

# LATER: status: str|Enum|something_else?
# - check what kind of status always appear over most projects


class SstFile(BaseModel):
    """Local file for upload and usage in prompt"""

    local_path: Path  # relative from local filedir
    keywords: set = Field(default_factory=set)

    # Timestamps
    first_tracked: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    @property
    def is_temp_file(self) -> bool:
        # IDEA: check if maybe needed
        # - for temporary instance without local_path?
        return self.local_path == Path(".")

    @property
    def name(self) -> str:
        return self.local_path.name

    @property
    def stem(self) -> str:
        return self.local_path.stem

    def touch(self) -> datetime:
        self.last_updated: datetime = datetime.now()
        return self.last_updated

    # TODO: get file by keyword

    def confirm_local_status(self, local_dir: Path) -> bool:
        file_path: Path = local_dir / self.local_path
        if not file_path.is_file():
            if not file_path.exists():
                msg: str = f"Nothing found at: {file_path=}"
            else:
                msg: str = f"No file found but exists: {file_path=}"
            logger.warning(msg)
            return False
        # LATER: check for changes, hash, etc
        return True
