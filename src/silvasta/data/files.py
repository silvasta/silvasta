from datetime import datetime

from pydantic import BaseModel, Field


class Course(BaseModel):
    """Course with all client information"""

    # NEXT: check with sachmis and shmoodle
    # REMOVE: place this here when actually used somewhere else
    name: str  # Clean name without year, e.g. "Game Theory and Control"
    id: int = 0  # unique? course ID
    semester: str = ""  # e.g. "HS25"
    short: str = ""  # e.g. "GTC" for "Game Theory and Control"
    is_active: bool = True


class SstFile(BaseModel):
    """Local file for upload and usage in prompt"""

    name: str  # TODO: define excact meaning
    # category: str  # WARN: under development, may change soon
    # topic: str  # WARN: under development, may change soon
    # TODO: status: str|Enum|something_else?
    # TODO: local_path: Path  # relative from local filedir

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    # updated_at: datetime = Field(default_factory=datetime.now) #TODO: how to save?
