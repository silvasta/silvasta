"""
Define the Objects that Shape and Assemble the Core

Meta
- Constructor: Meta Director
    - assemble: dynamic release (future)
- Meta: MetaClass Blueprint
- MetaData: InputSpace Guard
  - MetaInput: class specific unit -> single meta arg - dto
- Module: _meta

Class
- Builder: Compose the Mixins
  - compose: method (specialized, mixin custom defaults)
  - build: method
- Injector: Into the Target
- aggregate: method(or builder)
- draw: generate and write the stub files
- Module: _compose

Unit
- Factory: Build and Produce
  - produce: method (standardized input -> unit)
- _Forge: precise production
- Module: depending on purpose and location

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
    "Builder",
    "Constructor",
    "Injector",
]

from ._sketch import Builder, Constructor, Injector
