from typing import Protocol as Protocol

from .config import ProjectInfo


class Printer(Protocol):
    def set_project_info(self, project_info: ProjectInfo) -> None: ...
