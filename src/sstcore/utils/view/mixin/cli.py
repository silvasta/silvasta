"""
Compose CliMixins

- Atomize: 1 class with 1 method __cli__

"""

from typing import Any

from ..dto import LineDTO, PanelDTO

# IDEA: use some _specific_attribute(self):return "default" for override


def _name_or_cls_name(self):  # IDEA: unsure if that pays off...
    return getattr(self, "name", type(self).__name__)  # COLLECT: .base


class CliFullPanelMixin:
    def __cli__(self) -> PanelDTO:
        title: str = getattr(self, "name", type(self).__name__)
        data: dict[str, Any] = vars(self)
        return PanelDTO(
            title=title, content="Data", metrics=data, frame="cyan"
        )


class CliSlimPanelMixin:
    def __cli__(self) -> PanelDTO:  # TODO: at least something...
        title: str = getattr(self, "name", type(self).__name__)
        return PanelDTO(title=title, content="", metrics={}, frame="cyan")


class CliPanelMixin:
    def __cli__(self) -> PanelDTO:
        title = f"🏷️ {type(self).__name__}"  # NOTE: experimental
        if hasattr(self, "name"):
            title += f": {self.name}"

        metrics: dict[str, Any] = {  # COLLECT: .base
            k: v for k, v in vars(self).items() if not k.startswith("_")
        }
        return PanelDTO(
            title=title,
            content="Resource Data Metrics",
            metrics=metrics,
            frame="blue",
        )


class CliLineMixin:
    def __cli__(self) -> LineDTO:
        return LineDTO(message=str(self), style="cyan")
