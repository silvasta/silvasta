"""
First Sketch of a strategic Blueprint for the Assembler

Library Info
- sstcore/main: only data for publish
- sstcore/core: condenser for main and history, sketches, todos (marked with ___filename.py)
- sstcore/some: outer layer everything allowed, todos like _TODO_registry.py
Right now we are in the 'Outer Layer' (ugly details drop on the way to the inner branches)


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
    "Meta",
    "MetaData",
    "Composer",
    "Injector",
    # NEXT: "StubWriter",
    "Factory",
]


from typing import Any, Protocol, Self, overload


class _Constructor(Protocol):  # LATER: this as Meta Head Organizer
    """Engineer Meta Planning and Distribution"""

    def release(self, *args, **kwargs) -> str:
        """Assemble Blueprint Creators"""


class Meta(Protocol):
    """Assemble Blueprints for Classes"""

    def __new__(
        mcls,
        name: str,
        bases: Mixins,
        namespace: dict[str, Any],
        data: MetaData | None = None,
    ):
        """Define the Shape and Behaviour of the new Class"""

    @property
    def _data(self) -> MetaData: ...


class MetaData(Protocol):
    """InputSpace, Defaults, Pre-processing"""

    def __init__(self):
        """Ensure defaults for Meta.__new__"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### """Class Level - Create the Class"""
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

type Mixins = tuple[type, ...]


# NEXT:
class Composer[BaseT: type](Protocol):
    """Assemble Mixins dynamically and provide assembled Class"""

    @property
    def mixins(self) -> Mixins:
        """Provide all selected Mixins"""

    def mix_name(self, name: str = "") -> str:
        """Format Name of mixed class"""

    def build(self) -> BaseT:
        """Create a purely generic Base Mixin Class"""

    def inject[Target: type](self, cls: Target, **kwargs: Any) -> Target:
        """Inject mixins into an existing Class to form a new Subclass"""

    @overload
    def mix[TargeT](self, cls: type, mixins: Mixins) -> TargeT: ...
    @overload
    def mix(self, mixins: Mixins) -> BaseT: ...

    def mix[TargeT](self, cls: type | None = None, **kwargs) -> BaseT | TargeT:
        """Build new Class from Mixins or Inject to Target for new Subclass"""


# NEXT:
# NEXT:


class Injector[BaseT: type](Protocol):  # TODO: derive?
    """Decorate Target Class and Inject composed Mixins"""

    @overload
    def __call__[TargeT](self, cls: TargeT, /) -> TargeT: ...
    @overload
    def __call__(self, /) -> BaseT: ...
    def __call__(self, cls: type | None = None, /) -> type:
        """Inject Mixins to Target including changeable Presets"""

    def plus(self) -> Self:
        # TODO: ?? def plus(self, *args, **kwargs) -> Self:
        """Update existing Mixin selection"""


class StubWriter(Protocol):  # LATER: soon
    """Supply the Static Type Checker with Information"""

    # TASK: as soon as AST scanner ready:
    # - "invert" the process which for now looks like much easier
    # looks so far less painful than any already failed attempt...
    def draw(self):
        """Write .pyi for selected Mixins"""


class _Aggregator(Composer, Protocol):  # LATER: if ever needed...
    """Massively collect and assemble Mixins at Runtime"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### """Unit Level - Create the Instances"""
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Factory[UniT](Protocol):
    """
    Massively produce Units

    - Provide palette with default classes and arguments
    - optional: order new compositions to produce
    """

    def __call__(self, *args, **kwargs) -> UniT:
        """Produce Unit specialized on the purpose"""
