"""
Define the Shape of Exceptions

- SstError: The Root

                                                           ModuleLevel[0]
"""

__all__: list[str] = [
    "SstError",
]

from typing import Any

from ..contract.cli import PanelDTO, Renderable
from ..contract.log import LogDTO
from ..format.string import cls_name
from ..utils.color import ColorBox  # WARN: ColorBox???

c: ColorBox = ColorBox.bold()


class SstError(Exception):
    """Define the View and Behaviour of Custom Errors"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Store Kwargs as builtins.Exception forced handles Args"""
        self.kwargs: dict = kwargs
        super().__init__(*args)

    def _modify_scroll(self, lines: list[Renderable]) -> list[Renderable]:
        """Customize Lines displayed inside CLI Panel"""
        return lines

    @property
    def _short(self) -> str:
        """Set Optional Content for Header Line in CLI Panel"""
        return ""

    def __cli__(self) -> PanelDTO:
        """Provide Data Transfer Object for Command Line Interface"""

        lines: list[Renderable] = [
            # LATER: better table creation, similar to dict-like approach:
            # - title: text starting at predefined length
            # - use f-string with length cut, maybe by longest title or default
            # - difficulty: sorting! derived errors want to modify order
            f"{c.r(self.name)} {self.summary()}",  # ignore empty space
            f"{c.c('args')}    {self.args or 'nothing attached'}",
            f"{c.c('kwargs')}  {self.kwargs or 'nothing attached'}",
            *("" if self._causing_error else []),  # \newline or nothing
            *(self._causing_error if self._causing_error else []),
        ]

        return PanelDTO(
            text=self._modify_scroll(lines),
            title=self.__rich__(),
            frame="red",
            title_align="right",
        )

    @property
    def _causing_error(self) -> list[Renderable]:
        scroll_for_error_that_caused_this_error: list[Renderable] = []
        if reraised_error := (self.__cause__ or self.__context__):
            scroll_for_error_that_caused_this_error += [
                f"{c.r('ReRaised')} {c.r(cls_name(reraised_error))}",
                f"{reraised_error}",
            ]
        return scroll_for_error_that_caused_this_error

    def summary(self, *_args, max_len=60, **_kwargs) -> str:
        """Cut header line to ensure max length"""
        header_len: int = len(self.name) - 1 - len(self._short)
        if (to_long := max_len - header_len) < 0:
            # LATER:: create entire header? use f-string < max_len
            # something like: header = f"{f'{self.name} {self._short}': < 60}"
            return f"{self._short[: (to_long - 3)]}..."
        return self._short

    @property
    def name(self) -> str:
        """Provide ClassName ( __str__ already used for message builtins.Exception"""
        return cls_name(target=self)

    def __rich__(self) -> str:
        """Provide colorized Name"""
        # LATER: improve color hack, maybe by CamelCase?
        return f"{self.name[:-5]}{c.red('Error')}"

    def __repr__(self):
        """Provide Structured Data flattened to string"""
        attributes: list[str] = [f"args={self.args!r}"]
        attributes.extend(
            f"{k}={v!r}"
            for k, v in vars(self).items()
            if not k.startswith("_")
        )
        return f"{self.name}({', '.join(attributes)})"

    def __log__(self) -> LogDTO:
        """Provide Structured Data for Log"""
        return LogDTO(
            message=f"{self}" or self.name,
            level="ERROR",
            metrics={"args": self.args, "kwargs": self.kwargs},
            extra={"error_type": self.name},
        )
