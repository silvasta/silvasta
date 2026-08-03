"""
Provide Container for Names and tools for name composition

- Serialize with Settings and distribute with ConfigManager
- Provide small subset for SstPaths and other sstcore elements
- TBD: Hold pattern strings and tools for (bidirectional) Naming

                                                       DependencyLevel[0]
"""

from typing import TYPE_CHECKING

__all__: list[str] = [
    "SstNames",
]

from functools import cached_property

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from ..format.name import ParsedName
from ..port.config import Names as Names_
from ..port.view import Stringable
from ..utils import day_count


class SstNames(BaseSettings):
    """Provide static and dynamic names created with parsing tools"""

    model_config = ConfigDict(extra="allow")

    # Directories in local root
    data_dir: str = "data"
    plot_dir: str = "plots"

    # Files
    scanner_cache_file: str = ".sst_scanner_cache.json"

    @cached_property
    def _summary_file(self) -> ParsedName:
        return ParsedName(pattern="{day}_summary.{suffix}")

    def summary_file(self, day: Stringable = "", suffix: str = "md") -> str:
        return self._summary_file(
            target={"day": day or day_count(), "suffix": suffix.lstrip(".")}
        )


if TYPE_CHECKING:
    _instance_check: Names_ = SstNames()
    _class_check: type[Names_] = SstNames
