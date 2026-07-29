"""
Provide shared utils for Mixins.

- str/rich or log/repr will need it

"""

__all__: list[str] = [
    "MixinSentinel",
    "name",
    "rich",
    "data",
]

from typing import Any

from loguru import logger
from pydantic import BaseModel

from ....port import CliDTO, LogDTO, RichRenderable


class MixinSentinel:
    """Imitate a Mixin to replace None in View selection pipeline"""

    def __cli__(self) -> CliDTO:
        raise NotImplementedError

    def __log__(self) -> LogDTO:
        raise NotImplementedError

    def __rich__(self) -> RichRenderable:
        raise NotImplementedError


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Extractor
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def name(self: Any) -> str:
    """Check attribute list, provide match or default"""
    for guess in ["_inside_brackets", "_name", "name"]:
        if name := getattr(self, guess, ""):
            return name
    return " 󰂒 "


def text(self: Any, attrs: list | None = None) -> str | None:
    """Check if text in attribute list, provide match or None"""
    for guess in (attrs or []) + ["_text", "text"]:
        if name := getattr(self, guess, ""):
            return name
    return None


def rich(self: Any):  # MOVE: to sstcore.format?
    """Provide __rich__ value or default to __str__"""
    try:
        if hasattr(self, "__rich__"):
            return self.__rich__()
    except Exception as error:
        logger.error(f"Problem while formatting {self}: {error}")

    return str(self)


def data(self: Any, exclude: set[str] | None = None) -> dict[str, Any]:
    """Extract public data filtered by exclude"""

    exclude: set[str] = exclude or set()

    if isinstance(self, BaseModel):
        return self.model_dump(exclude=exclude)

    return {
        k: v
        for k, v in vars(self).items()
        if not k.startswith("_") and k not in exclude
    }


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Helper
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def dict_to_list(data: dict[str, Any], sep="=") -> list[str]:
    """Format each dict entry to string with separator"""
    return [
        f"{key}{sep}{value}"  #
        for key, value in data.items()
    ]


def list_to_str(strings: list[str], sep=", ") -> str:
    """Concat list of string with separator"""
    return f"{sep}".join(strings)


def dict_to_str(data: dict[str, Any], inner="=", outer=", ") -> str:
    """Concat all formatted entries of dict to single string"""
    strings: list[str] = dict_to_list(data, sep=inner)
    return list_to_str(strings, sep=outer)
