from typing import Any

import fire
from pydantic import BaseModel

from sstcore import printer
from sstcore.events.dto import PanelDTO
from sstcore.events.protocol import CliDTO, CliRenderable


def main():
    fire.Fire(LaunchDTO)


class LaunchDTO:
    def panel(self):
        unwrap_panel(LLMConversationAgent())


class LLMConversationAgent(BaseModel):
    name: str = "sachmis"
    system_prompt: str = "bla bla..\n" * 500
    message_history: list[dict] = []
    tokens_used: int = 25
    is_active: bool = True

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            title=f"Agent: {self.name}",
            content="create proper DTO first",
            metrics={
                "Tokens": self.tokens_used,
                "Messages": len(self.message_history),
            },
            frame="yellow",
        )


def unwrap_panel(target: Any):
    printer("start of panel target")

    if hasattr(target, "__cli__"):
        printer.yellow("target hasattr")
        dto: CliDTO = target.__cli__()
        if isinstance(dto, PanelDTO):
            printer.lines(
                lines=[f"{k}: {v}" for k, v in dto.metrics.items()],
                header=dto.content,
                title=dto.title,
                style=dto.frame,
            )
    if isinstance(target, CliRenderable):
        printer.green("target is CliRenderable")
        dto: CliDTO = target.__cli__()
        if isinstance(dto, PanelDTO):
            printer.title(
                text=[f"{k}: {v}" for k, v in dto.metrics.items()],
                title=dto.title,
                style="green",
            )
    printer.line()
    printer("send target into printer")
    printer(target)


if __name__ == "__main__":
    main()
