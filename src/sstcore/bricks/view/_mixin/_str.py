"""
Compose StrMixins

- Atomize: 1 class with 1 method __str__

"""

__all__: list[str] = [
    "SimpleNameMixin",
    "NameMixin",
    "ModuleNameMixin",
]

from ....bricks.format import cls_name, reflect


class SimpleNameMixin:
    """Show class name"""

    def __str__(self) -> str:
        return cls_name(self)


class NameMixin:
    """
    Show colorized class name and attribute value as below

    - _inside_brackets (priority 1, descending)
    - _name
    - name
    """

    def __str__(self) -> str:
        return f"{cls_name(self)}[{reflect.name(self)}]"


class ModuleNameMixin:
    """Show module path from project to class name"""

    def __str__(self) -> str:
        return self.__module__
