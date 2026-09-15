"""
Define the Assembler that Shape the Objects of the Core

- First Strategic Blueprint of the Assembler Definitions

                                                 DependencyLevel[0]

---

Meta - Home: brick.forge.blueprint

- Meta: MetaClass Blueprint
- MetaData: InputSpace DTO (and Guard?)
  - MetaInput: name for class specific implementation
- Local Module: _meta (if ever needed again, the dto collapsed everything)

---

Class - Home: brick.forge.mix

- Composer: Assemble the Mixins
- Methods:
  - mix: dispatch composition
    - build: compose new class from mixins and bases
    - inject: compose and inject to existing class
- Local Module: _compose

- Injector: Compose and sit on Functions and Classes
  Method: __call__,
  Module: _inject

- Writer: read the manual and write the stub file
- Methods:
  - draw|print: release the final stub file
    maybe others, generate, display, validate,...

---

Instances - Home: brick.forge.unit

- Factory: Massively produce Units ordered by catalogue

- Producer: designed to create specialized units, e.g. LogDtoProducer
  - Method: __call__, produce units
  - Module: _produce

- Depending on purpose: individual modules, functions and names

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

Status:
meta
- Soon: Scanner: maybe StaticFunctor
- Later: Format/Normalize: maybe StaticFunctor

class
- Now: PrintBuilder: outdated status (maybe PrintForge)
    - Soon: EmitBuilder: will share most of mixins with Printer (like +1 new, -5 old)
- Now: FileRegistryBuilder: in progress
- Later: Registry(Injector|Builder) so far they are mixed in like everywhere, could be automated
- Done: ViewInjector: best example so far (this is like an aggragator)

unit
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
    """Single DTO Interface - InputSpace, Defaults, Pre-processing"""

    def __init__(self):
        """Ensure Meta.__new__ defaults and bundle valid injection"""


#  LINE: -- Class Level -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type Mixins = tuple[type, ...]


class Composer[BaseT: type](Protocol):
    # NEXT: composer finish!
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


class Injector[BaseT: type](Protocol):  # TODO: derive?
    # NEXT: injector finish!
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


class StubWriter(Protocol):
    # IMPORTANT: generate stubs
    # TASK: as soon as AST scanner ready:
    # - read and understand the composer process
    #   - the mixins that come in, especially the protocols!
    # - ast and cst
    # - write the specific pyi file
    #   - location and (automatic) updates
    # - Validation?
    """Supply the Static Type Checker with Information"""

    def draw(self):
        """Write .pyi for selected Mixins"""


#  LINE: -- Unit Level -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Factory[UniT](Protocol):
    """
    Massively produce Units

    - Provide palette with default classes and arguments
    - optional: order new compositions to produce
    """

    def __call__(self, *args, **kwargs) -> UniT:
        """Produce Unit specialized on the purpose"""
