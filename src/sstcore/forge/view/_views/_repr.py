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


from ....brick import reflect
from ....brick.format import norm
from ....brick.reflect import scan


class ReprMixin:
    """Show class name and [box] with custom data or default to public attrs"""

    @property
    def _repr_box_text(self):
        """Provide subhook for override __repr__ [box text]"""
        return norm.dict_to_str(scan.pydantic(self))

    def __repr__(self) -> str:
        return f"{reflect.clsname(self)}[{self._repr_box_text}]"


class ReprDataMixin:
    """Show all public attributes"""

    def __repr__(self) -> str:
        return (
            f"{reflect.clsname(self)}({norm.dict_to_str(scan.pydantic(self))})"
        )


class FullReprMixin:
    """Show all attributes"""

    def __repr__(self) -> str:
        return f"{reflect.clsname(self)}({norm.dict_to_str(vars(self))})"
