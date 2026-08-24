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


class MixData(Protocol):  # REMOVE: most of them only in Implementation
    # IDEA: build data, maybe as 1 dto with mixin registry??
    # - MixinData?
    name: str
    format_name: bool
    extras: dict | None
    # Mixin data (maybe include in new tuple registry)
    prepend: bool = True


class Composer[BaseMixType: type](Protocol):
    """Assemble Mixins dynamically and provide assembled Class"""

    def mix_name(self, name: str = "") -> str:
        """Format Name of mixed class"""

    @property
    def mixins(self) -> tuple[type, ...]:
        """Provide all selected Mixins"""

    # TODO: overloads dispatch on cls
    @overload
    def mix[MixInjected](
        self,
        cls: type,
        mixins: tuple[type, ...],
        data: MixData,
    ) -> MixInjected: ...
    @overload
    def mix(
        self,
        mixins: tuple[type, ...],
        data: MixData,
    ) -> BaseMixType: ...

    def mix[MixInjected](  # # TODO: maybe insert here mixed proto? for cast?
        self,
        cls: type | None = None,
        *,
        # AI: Maybe send mixins as TupleRegistry, but then:
        # - overload for sending mixins standalone!
        mixins: tuple[type, ...],
        data: MixData,
    ) -> BaseMixType | MixInjected:
        """Build new Class from Mixins or Inject to Target for new Subclass"""


class Injector[BaseMixType: type](Protocol):  # TODO: derive?
    """Decorate Target Class and Inject composed Mixins"""

    @overload
    def __call__[MixInjected](self, cls: MixInjected, /) -> MixInjected: ...
    @overload
    def __call__(self, /) -> BaseMixType: ...
    def __call__(self, cls: type | None = None, /) -> type:
        """Inject Mixins to Target including changeable Presets"""

    def plus(self, *args, **kwargs) -> Self:
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
