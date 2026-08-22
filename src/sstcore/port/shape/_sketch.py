"""
First Sketch of a strategic Blueprint for the Assembler

Library Info
- sstcore/main: only data for publish
- sstcore/core: condenser for main and history, sketches, todos (marked with ___filename.py)
- sstcore/some: outer layer everything allowed, todos like _TODO_registry.py
Right now we are in the 'Outer Layer' (ugly details drop on the way to the core and again to main)


Implementations
- Soon: Scanner: maybe StaticFunctor
- Later: Format/Normalize: maybe StaticFunctor

- Now: PrintBuilder: outdated status (maybe PrintForge)
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


class Constructor(Protocol):
    """Engineer of Meta Planning and Distribution"""

    def assemble(self, *args, **kwargs) -> str:
        """Launch the Blueprints"""


class Meta(Protocol):
    """Blueprint for Classes"""

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: MetaData | None = None,
    ):
        """MetaInput = MetaData(customize with functions and values)"""


class MetaData(Protocol):
    """InputSpace, Defaults, Pre-processing -> finally data container"""


class Builder[Mix: type](Protocol):
    """Aggreggate Mixins dynamically and compile them into a Class"""

    @property
    def mixins(self) -> tuple[type, ...]:
        """Provide all selected Mixins"""

    def mix_name(self, name: str = "") -> str:
        """Format the Name of the mixed class"""

    def build(self, name: str, format_name: bool, extras: dict | None) -> Mix:
        """Assemble the selected Mixins to a new Class"""

    def compose(self) -> Self:
        """Merge custom mixins, overrides, and defaults"""


class _Aggregator(Builder, Protocol):  # LATER: not soon in planning
    def aggregate(self):
        """Massively collect and assemble Mixins at Runtime"""


class StubWriter(Protocol):  # LATER: but soon
    def draw(self):
        """Write .pyi from Mixin stack, parallel or as Builder"""


class Injector[Mix: type, TargetClass: type](Builder[Mix], Protocol):
    """Compose Mixins and Inject to existing TargetClass"""

    def inject(self, cls: TargetClass) -> TargetClass:
        """Inject the selected Mixins to new Subclass of Target"""

    @overload
    def __call__(self, cls: TargetClass, /) -> TargetClass: ...

    @overload
    def __call__(self, /) -> type: ...

    def __call__(self, cls: type | None = None, /) -> type:
        """Inject composed mixins to Decorated target or Build class"""


class Factory[UniT](Protocol):
    """Massively fabric units and build them if needed"""

    def produce(self) -> UniT:
        """Launch Units"""


class _Forge[UniT](Protocol):  # TODO: check for Printer
    """Create custom-made products"""

    def smith(self) -> UniT:
        """Launch Unit"""
