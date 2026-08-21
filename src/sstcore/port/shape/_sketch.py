"""
First Sketch of a strategic Blueprint for the Assembler

Library Info
- sstcore/main: only data for publish
- sstcore/core: condenser for main and history, sketches, todos (marked with ___filename.py)
- sstcore/some: outer layer everything allowed, todos like _TODO_registry.py
Right now we are in the outer layer (ugly details drop on the way to the core and again to main)


Implementations
- Soon: Scanner: maybe StaticFunctor
- Later: Format/Normalize: maybe StaticFunctor

- Now: PrintBuilder: outdated status
    - Soon: EmitBuilder: will share most of mixins with Printer (like +1 new, -5 old)
- Now: FileRegistryBuilder: in progress
- Later: Registry(Injector|Builder) so far they are mixed in like everywhere, could be automated
- Done: ViewInjector: best example so far (this is like an aggragator)

- Now: ColorFactory
- Now: DtoFactory

"""

__all__: list[str] = [
    "Builder",
    "Constructor",
    "Injector",
]


from typing import Any, Protocol, Self, overload


# INFO: META
class Constructor(Protocol):
    """The Architect/Engineer of the Meta Planning"""

    # NOTE: Specific Meta follow later if ever desired


# INFO: Class
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


# NOTE: Someone will grab the mixins and write the CST


# INFO: Class
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


# INFO: Unit
class Factory[MixInstance](Builder[type[MixInstance]], Protocol):
    """Massively provide Instances and build if needed"""

    def produce(self, *args, **kwargs) -> MixInstance:
        """Build and Produce the Units"""

    # NOTE: most classes usually produced where created or needed
