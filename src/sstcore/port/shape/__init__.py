"""
Define the Objects that Shape and Assemble the Core

Meta
- Constructor: Design the Structure
- XxxMeta: Blueprint Xxx MetaClass
- XxxMetaData: Guard Xxx InputSpace
  XxxMetaInput: class specific setup (Data -> Input -> class arg -> class data)
  (Eliminates problems at the highest level truly foolproof)
- _assemble: method
- _meta: module
- _blueprint: module

Class
- YyyBuilder: Compose the Mixins
- YyyInjector: Into the Target
- compose: method (specialized, mixin custom defaults)
  (compose|build still somehow conflicting...)
- build: method (simple, countable mixins, clear instructions for assembly)
- aggregate: method (massively dynamic mixin assembly)
- _compose: module
- draw: generate and write the stub files
  (most likely easier to forward parse mixin list than for the type checker to backwards identify them)

Unit
- ZzzFactory: Build and Produce (massivly released units)
- create: method (specialized input -> unit)
- produce: method (standardized input -> unit)
- _produce: module (massively)
- _factory: module (build and produce)
- _forge: module (specialized)

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

from ._core import Builder, Constructor, Injector
