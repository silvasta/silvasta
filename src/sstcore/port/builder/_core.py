"""
Define a Blueprint for the Builders

Implementations
- Printer: outdated status
- ViewBuilder: best example so far
- FilesBuilder: in progress

"""

__all__: list[str] = [
    "Builder",
    "Constructor",
    "Injector",
]


from typing import Any, Protocol, Self, overload


class Builder[Mix: type](Protocol):
    """Aggreggate Mixins dynamically and compile them into a Class"""

    @property
    def mixins(self) -> tuple[type, ...]:
        """Provide all selected Mixins"""

    def mix_name(self, name: str = "") -> str:
        """Format the Name of the mixed class"""

    def build(self, name: str, format_name: bool, extras: dict | None) -> Mix:
        """Assemble the selected Mixins to a new Class"""

    def compose(self, *args: Any, **kwargs: Any) -> Self:
        """Merge custom mixins, overrides, and defaults"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
###  Level 1
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Constructor[MixInstance](Builder[type[MixInstance]], Protocol):
    """Assemble the Mixins and provide Instances"""

    def construct(self, name="", **init_kwargs: Any) -> MixInstance:
        """Build and Instanciate the selected Mixins"""


class Injector[Mix: type, TargetClass: type](Builder[Mix], Protocol):
    """Assemble the Mixins and Inject to existing TargetClass"""

    def inject(self, cls: TargetClass) -> TargetClass:
        """Inject the selected Mixins to new Subclass of Target"""

    @overload
    def __call__(self, cls: TargetClass, /) -> TargetClass: ...

    @overload
    def __call__(self, /) -> type: ...

    def __call__(self, cls: type | None = None, /) -> type:
        """Inject composed mixins to Decorated target or Build class"""
