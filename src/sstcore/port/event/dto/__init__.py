"""
Provide Data Transfer Objects for the EventBus

- EventDTO: root
- LogDTO  Intended for __log__ and processed by logger
- CliDTO: Intended for __cli__ and processed by printer

"""

__all__: list[str] = [
    "EventDTO",
    #
    "LogDTO",
    "CliDTO",
    "Renderable",
    # cli derivatives
    "PanelDTO",
    "LineDTO",
    "GroupDTO",
    "TableDTO",
    "MarkdownDTO",
    "RuleDTO",
]
from ._base import EventDTO
from ._cli import CliDTO, Renderable
from ._cli_group import GroupDTO, LineDTO, PanelDTO, RuleDTO
from ._cli_table import MarkdownDTO, TableDTO
from ._log import LogDTO
