"""
View Assembly

.
"""

from ...brick import reflect
from ...brick.format import norm


class FieldView:
    def __str__(self) -> str:
        return f"[({reflect.clsname(self)})][{reflect.name(self)}]"

    def __repr__(self) -> str:
        return f"{self}({norm.dict_to_str(vars(self))})"
