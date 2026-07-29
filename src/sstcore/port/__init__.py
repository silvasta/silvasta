"""
Define the Shape and Structure of Functions and Classes.

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "Event",
    "EventPattern",
    "EmitFunc",
    "EventName",
    "CliEvent",
    "CoreEvent",
    # base dtos
    "LogDTO",
    "CliDTO",
    # derive cli dtos
    "PanelDTO",
    "LineDTO",
    "GroupDTO",
    "TableDTO",
    "MarkdownDTO",
    "RuleDTO",
    #
    "CliRenderable",
    "Stringable",
    "RichRenderable",
    "ReprRenderable",
    "LogSerializable",
    "Renderable",
]

from ._cli import (
    CliDTO,
    CliRenderable,
    GroupDTO,
    LineDTO,
    MarkdownDTO,
    PanelDTO,
    Renderable,
    RichRenderable,
    RuleDTO,
    TableDTO,
)
from ._event import (
    CliEvent,
    CoreEvent,
    EmitFunc,
    Event,
    EventName,
    EventPattern,
)
from ._log import LogDTO, LogSerializable
from ._native import ReprRenderable, Stringable
