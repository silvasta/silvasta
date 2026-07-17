"""
Compose StrMixins

- Atomize: 1 class with 1 method __str__
"""


class SimpleNameMixin:  # TODO: synchronize with rich, use StyledName
    def __str__(self) -> str:
        return type(self).__name__


class NameMixin:  # TODO: synchronize with rich, use StyledName
    def __str__(self) -> str:
        name: str = getattr(self, "name", "NoName")
        # IDEA: same as in .cli: define some _get_param for override or default
        return f"{type(self).__name__}[{name}]"  # LATER: brackets
