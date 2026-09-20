"""
Compose ReprMixins

- Atomize: 1 class with 1 method __repr__

                             DependencyLevel.sstcore.brick.views[0]
"""

__all__: list[str] = [
    "ReprMixin",
    "ReprDataMixin",
    "FullReprMixin",
]


from ..labor import reflect
from ..norm import transform


class ReprMixin:
    """Show class name and [box] with custom data or default to public attrs"""

    @property
    def _repr_box_text(self):
        """Provide subhook for override __repr__ [box text]"""
        return transform.dict_to_str(reflect.pydatic(self))

    def __repr__(self) -> str:
        return f"{reflect.clsname(self)}[{self._repr_box_text}]"


class ReprDataMixin:
    """Show all public attributes"""

    def __repr__(self) -> str:
        return f"{reflect.clsname(self)}({transform.dict_to_str(reflect.pydatic(self))})"


class FullReprMixin:
    """Show all attributes"""

    def __repr__(self) -> str:
        return f"{reflect.clsname(self)}({transform.dict_to_str(vars(self))})"
