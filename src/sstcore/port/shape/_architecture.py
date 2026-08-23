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
    "Meta",
    "MetaData",
    "Composer",
    "Injector",
    "Factory",
]


from typing import Any, Protocol, Self, overload


class Constructor(Protocol):  # LATER: this as Meta Head Organizer
    """Engineer Meta Planning and Distribution"""

    def release(self, *args, **kwargs) -> str:
        """Assemble Blueprint Creators"""


class Meta(Protocol):
    """Assemble Blueprints for Classes"""

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
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


class Composer[Base: type](Protocol):
    """Assemble Mixins dynamically and provide assembled Class"""

    def mix_name(self, name: str = "") -> str:
        """Format Name of mixed class"""

    @property
    def mixins(self) -> tuple[type, ...]:
        """Provide all selected Mixins"""

    def build(
        self,
        name: str,
        format_name: bool,
        extras: dict | None,
        *,
        mixins: tuple[type, ...],
        prepend: bool,
    ) -> Base:
        """Compose combined Mixins to new Class"""

    def inject[Target: type](
        self,
        cls: Target,
        /,
        *mixins: type,
        prepend: bool = True,
    ) -> Target:
        """Inject combined Mixins to new Subclass of Target"""

    # @overload
    # def __call__(self, cls: Mixed, **kwargs) -> Mixed: ...
    # @overload
    # def __call__(self, **kwargs) -> Base: ...
    # def __call__(self, cls: type | None = None, **kwargs) -> type:
    #     """Compose mixins and if provided, inject to inserted cls"""


class Injector[Base: type, Mixed: type](Protocol):
    """Decorate Target Class and Inject Compose Mixins"""

    # def __call__(self, cls: type | None = None, /) -> type:
    #     """Inject Mixins to decorated Target or just compose"""

    def plus(self, *args, **kwargs) -> Self:
        """Update existing Mixin selection"""

    @overload
    def __call__(self, cls: Mixed, /) -> Mixed: ...
    @overload
    def __call__(self, /) -> Base: ...
    def __call__(self, cls: type | None = None, /) -> type:
        """
        Inject Mixins to decorated Target or build bare class

        -
        """


class Documenter(Protocol):
    # TASK: as soon as AST scanner ready:
    # - "invert" the process which for now looks like much easier
    # looks so far less painful than any already failed attempt...
    """Supply the Static Type Checker with Information"""

    def draw(self):
        """Write .pyi for selected Mixins"""


class _Aggregator(Composer, Protocol):  # LATER: if ever needed
    def aggregate(self):
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
