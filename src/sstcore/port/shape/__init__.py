"""
Define the Objects that Shape and Assemble the Core

Meta
- Constructor: Meta Director
    - assemble: dynamic release (future)
- Meta: MetaClass Blueprint
- MetaData: InputSpace Guard
  - MetaInput: class specific unit -> single meta arg - dto
- Global location: brick.meta
- Local Module: _meta

Class
- Composer: Assemble the Mixins
  - Method: __call__ BUT check with Injector
  - draw: generate and write the stub files -> mixin for composer
  - Module: _compose
  - Module: _forge
- Injector: Into the Target

- aggregate: method(or builder)

Unit
- Factory: (Build and) Produce
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
