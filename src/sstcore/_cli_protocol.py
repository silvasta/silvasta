"""
Temporary Module!

Collect ideas for Log and Print extension:
- DTO (dataclass hardly prefered)
- Protocol (for easy filter and type safety)
- dunder (__cli__ and __log__ as extension to __str__,__repr__ and __rich__)
- log sink (from raw strings to json or db)
"""

# sstcore/utils/print/models.py
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class PanelDTO:
    """Standard 3-5 line summary for the Printer."""

    title: str
    status: str
    metrics: dict[str, Any] = field(default_factory=dict)
    frame_color: str = "cyan"


@dataclass
class LogDTO:
    """For simple, single-line structured outputs."""

    message: str
    level: str = "info"


# sstcore/utils/print/protocols.py
# from .models import PanelDTO, LogDTO


class CliRenderable(Protocol):
    def __cli__(self) -> PanelDTO | LogDTO: ...


# project/agent.py
from pydantic import BaseModel

from sstcore.utils.print.models import PanelDTO


class LLMConversationAgent(BaseModel):
    name: str
    system_prompt: str  # Massive 500-line string
    message_history: list[dict]  # Massive nested data
    tokens_used: int
    is_active: bool

    def __cli__(self) -> PanelDTO:
        """Condense the massive Pydantic model into a clean 3-line UI."""
        return PanelDTO(
            title=f"Agent: {self.name}",
            status="Active" if self.is_active else "Idle",
            metrics={
                "Tokens": self.tokens_used,
                "Messages": len(self.message_history),
            },
            frame_color="purple",
        )


# sstcore/utils/print/base.py
from .models import PanelDTO


class BasePrinter:
    # ...

    def render(self, target: Any, **kwargs):
        if hasattr(target, "__cli__"):
            dto = target.__cli__()

            if isinstance(dto, PanelDTO):
                lines = [f"{k}: {v}" for k, v in dto.metrics.items()]
                self.lines(
                    lines,
                    header=dto.status,
                    title=dto.title,
                    style=dto.frame_color,
                )
                return

        # If it doesn't have __cli__, or if you explicitly bypassed it for debugging,
        # it falls back to rich's default handling (great for full Pydantic dumps)
        self(target, **kwargs)


# IDEA: log
from loguru import logger

# In the core:
logger.opt(lazy=True).debug(
    "Current DAG State: \n{state}",
    # This lambda only runs if DEBUG is active!
    state=lambda: printer.format_tree(internal_dag),
)


class DataSingulationOperator:
    def __log__(self) -> LogDTO:
        return LogDTO(
            message=f"Singulator({self.active_items} items)", level="debug"
        )


# In a custom loguru sink or wrapper in sstcore:
def smart_log(obj, message=""):
    if hasattr(obj, "__log__"):
        dto = obj.__log__()
        # Route it to loguru with the requested level
        getattr(logger, dto.level)(f"{message} {dto.message}")
    else:
        logger.info(str(obj))
