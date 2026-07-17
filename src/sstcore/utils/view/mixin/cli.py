"""
Compose CliMixins

- Atomize: 1 class with 1 method __cli__

"""

from typing import Any

from ....contract.cli import LineDTO, PanelDTO

# IDEA: use some _specific_attribute(self):return "default" for override


def _name_or_cls_name(self):  # IDEA: unsure if that pays off...
    return getattr(self, "name", type(self).__name__)  # COLLECT: .base


class CliFullPanelMixin:
    def __cli__(self) -> PanelDTO:
        text = str(self)
        data: dict[str, Any] = vars(self)
        return PanelDTO(text=text, title="Data", metrics=data, frame="cyan")


class CliSlimPanelMixin:
    def __cli__(self) -> PanelDTO:  # TODO: at least something...
        text = str(self)
        return PanelDTO(text=text, title="Data", frame="cyan")


class CliPanelMixin:
    def __cli__(self) -> PanelDTO:
        title = f"🏷️ {self}"  # NOTE: experimental

        metrics: dict[str, Any] = {  # COLLECT: .base
            k: v for k, v in vars(self).items() if not k.startswith("_")
        }
        return PanelDTO(  # TODO: table
            text=title,
            metrics=metrics,
            frame="blue",
        )


class CliLineMixin:
    def __cli__(self) -> LineDTO:
        return LineDTO(text=str(self), style="cyan")
