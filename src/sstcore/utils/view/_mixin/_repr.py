"""
Compose ReprMixins

- Atomize: 1 class with 1 method __repr__
"""

__all__: list[str] = [
    "ReprMixin",
    "ReprDataMixin",
    "FullReprMixin",
]

from ....format.convert import dict_to_str
from ....format.reflect import cls_name
from ._basics import data


class ReprMixin:
    """Show class name and [box] with custom data or default to public attrs"""

    @property
    def _repr_box_text(self):
        """Provide subhook for override __repr__ [box text]"""
        return dict_to_str(data(self))

    def __repr__(self) -> str:
        return f"{cls_name(self)}[{self._repr_box_text}]"


class ReprDataMixin:
    """Show all public attributes"""

    def __repr__(self) -> str:
        return f"{cls_name(self)}({dict_to_str(data(self))})"


class FullReprMixin:
    """Show all attributes"""

    def __repr__(self) -> str:
        return f"{cls_name(self)}({dict_to_str(vars(self))})"
