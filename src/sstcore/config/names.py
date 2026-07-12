"""
Provide Container for Names and tools for name composition

- Serialize with Settings and distribute with ConfigManager
- Provide small subset for SstPahts and other sstcore elements
- TBD: Hold pattern strings and tools for (bidirectional) Naming

"""

from functools import cached_property

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from ..utils.parse import ParsedName, StyledName


class SstNames(BaseSettings):
    """Provide static and dynamic names created with parsing tools"""

    model_config = ConfigDict(extra="allow")

    project: str = "sstcore"

    # Directories in local root
    data_dir: str = "data"
    plot_dir: str = "plots"

    @cached_property
    def sstfile_dates(self) -> StyledName:
        # AI: here this huge monster should be much easier controllable
        return StyledName.parse_style(
            style_pattern=(
                "[{style1}]{name}[/]: [{style2}]{first_tracked}[/]"
                " - [{style3}]{last_updated}[/]"
            ),
            keys=["name", "first_tracked", "last_updated"],
            styles=["blue", "dim", "white"],
        )

    @cached_property
    def summary_file(self) -> ParsedName:
        return ParsedName(
            pattern="{day}_summary.{suffix}",
            keys=["day", "suffix"],
        )
