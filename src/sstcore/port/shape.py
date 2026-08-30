"""
Define the Assembler that Shape the Objects of the Core

- First Sketch of a strategic Blueprint for the Assembler
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

Meta
- Home: brick.forge.blueprint

- Constructor: Meta Director (future)
    - assemble: dynamic release (future)

- Meta: MetaClass Blueprint
- MetaData: InputSpace Guard
  - MetaInput: class specific unit -> single meta arg - dto
  - Local Module: _meta


Class
- Home: brick.forge.mix

- Composer: Assemble the Mixins
  Method:
  - build: compose new class from mixins and bases
  - inject: compose and inject to existing class
  - mix: dispatch build and inject
  - draw: generate and write the stub files -> mixin for composer
  Module: _compose

- Injector: Into the Target
  Method: __call__,
  Module: _inject


Unit
- Home: brick.forge.units

- Factory: (Order composition and) massively produce, e.g. DtoFactory
- Producer: designed to create specialized units, e.g. LogDtoProducer
  - Method: __call__, produce units
  - Module: _produce

- Plus: individual modules, functions and names, depending on purpose

---

Strategy:
  Done
  + Protocol support for Builder (as guidance, without obligation)
  + Consistent naming for builder: package, module, class, function
  + Basic infrastructur (mainly gatekeeper protocol for now)
  Soon
  - Collect best working concepts
  Final
  - The Generalized and Typed assemble Pipeline

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
