"""
Define the Assembler that Shape the Objects of the Core

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
  - build: compose new class only from mixins and bases
  - inject: compose and inject to existing class
  - mix: dispatch for build or inject
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
  Now
  - Protocol support for Builder (as guidance, without obligation)
  - Consistent naming for builder: package, module, class, function
  - Basic infrastructur (mainly gatekeeper protocol for now)
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
    "Factory",
]

from ._architecture import Composer, Factory, Injector, Meta, MetaData
