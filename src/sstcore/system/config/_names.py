"""
Provide Container for Names and tools for name composition

- Serialize with Settings and distribute with ConfigManager
- Provide small subset for SstPaths and other sstcore elements
- TBD: Hold pattern strings and tools for (bidirectional) Naming

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "SstNames",
]

from functools import cached_property

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from ...brick.format.name import NameParser
from ...brick.time import day_count
from ...port.config import Names
from ...port.link import portlink
from ...port.represent import Stringable


@portlink(Names)
class SstNames(BaseSettings):
    model_config = ConfigDict(extra="allow")

    # Directories in local root
    data_dir: str = "data"
    plot_dir: str = "plots"

    # Files
    scanner_cache_file: str = ".sst_scanner_cache.json"

    @cached_property
    def _summary_file(self) -> NameParser:
        return NameParser(pattern="{day}_summary.{suffix}")

    def summary_file(self, day: Stringable = "", suffix: str = "md") -> str:
        return self._summary_file(
            target={"day": day or day_count(), "suffix": suffix.lstrip(".")}
        )
