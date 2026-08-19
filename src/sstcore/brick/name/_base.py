"""
Provide view and basic functionalities for Names

                                                      DependencyLevel[0]
"""

__all__: list[str] = [
    "BaseName",
]


class BaseName:
    """Hold Meta and Views"""

    pattern: str
    keys: tuple[str, ...]

    @property
    def _name(self):
        return type(self).__name__

    @property
    def _color(self):
        return "cyan"

    def __str__(self):
        return f"{self._name}[:{len(self.keys)}]"

    def __repr__(self):
        return f"{self._name}[{self.keys}'{self.pattern}']"

    def __rich__(self):
        return f"[{self._color}]{self._name}[/][{self.keys}'{self.pattern}']"
