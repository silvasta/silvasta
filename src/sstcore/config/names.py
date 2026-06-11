from functools import cached_property

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from ..utils.parse import ParsedName, StyledName


class SstNames(BaseSettings):
    model_config = ConfigDict(extra="allow")

    project: str = "sstcore"

    # Directories in local root
    data_dir: str = "data"
    plot_dir: str = "plots"

    @cached_property
    def sstfile_dates(self) -> StyledName:
        # TODO: compare this with Printer and Colorbox -> find best setup
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
