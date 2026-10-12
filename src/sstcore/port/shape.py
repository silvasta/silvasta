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
- Local Package: blueprint

---

Class - Home: brick.forge.mix

- Builder: Assemble the Mixins
- Methods:
  - compose: dispatch composition
    - mix: compose new class from mixins and bases
    - inject: compose and inject to existing class
- Local Module: _compose
- Local Package: build

- Injector: Compose and sit on Functions and Classes
  Method: __call__,
  Module: _inject

- Typer: read the manual and write the stub file
- Methods:
  - sketch: draw, validate, display, write

---

Instances - Home: brick.forge.unit

- Factory: Massively produce Units ordered by catalogue

- Producer: designed to create specialized units, e.g. LogDtoProducer
  - Method: __call__, produce units
  - Module: _produce

- Depending on purpose: individual modules, functions and names

---
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
    "Builder",
    "Injector",
    "Typer",  # TODO:
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
        """Ensure Meta.__new__ defaults and valid injection"""


#  LINE: -- Class Level -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type Mixins = tuple[type, ...]


class Builder[BaseT: type](Protocol):  # LATER: KwargSpace as TypedDict
    """Assemble Mixins dynamically and provide assembled Class"""

    @property  # LATER: sort strategy, better than just prepend
    def mixins(self) -> Mixins:
        """Provide all selected Mixins"""

    def clsname(self, name: str = "") -> str:
        """Generate Name of Mixed Class"""

    def compose(self, *mixins: type) -> BaseT:
        """Create a purely generic Base Mixin Class"""

    def inject[Cls: type](self, cls: Cls, /) -> Cls:
        """Inject mixins into an existing Class to form a new Subclass"""


class Injector[BaseT: type](Builder, Protocol):
    """Decorate Cls Class and Inject composed Mixins"""

    @overload
    def __call__[Cls: type](self, cls: Cls, /) -> Cls: ...
    @overload
    def __call__[Cls: type](self, cls: Cls, /, *mixins: Any) -> Cls: ...
    @overload
    def __call__(self, *mixins: Any) -> Self: ...

    def __call__[Cls: type](
        self, cls: Cls | None = None, *mixins: type
    ) -> Any:
        """Inject Mixins to Cls including changeable Presets"""

    def plus(self, *mixins: Any) -> Self:
        # TASK: mixins:type? consider enum_catalog, maybe both
        """Update existing Mixin selection"""


class Typer[**P](Protocol):  # NEXT: generate stubs
    """Supply the Static Type Checker with Information"""

    def draw(self, *args: P.args, **kwargs: P.kwargs):
        # TODO: sketch: draw, validate, display, write
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
