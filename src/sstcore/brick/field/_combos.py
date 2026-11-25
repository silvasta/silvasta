"""
Assemble the first level of composed Fields

Prepare for direct Usage and as Base for further Specicications

- RequiredField: placeholder for dynamic typed value attach
- LazyField: placeholder with zero arg factory
- DerivedField: calculate with dynamic attributes
- Forward: direct access to inner attributes, Outer.access = Outer.Inner.access

                                                 DependencyLevel[2]
"""

from typing import Any

__all__: list[str] = [
    "RequiredField",
    "LazyField",
    "DerivedField",
    "Forward",
]


from ...port import attach
from ...port.attach import FieldLoader
from ...port.link import portlink
from ..reflect import funcname
from ._base import ReadField, WriteField
from ._extend import TypedField


@portlink(attach.ValidDescriptor)
class RequiredField[FieldT](ReadField[FieldT], TypedField[FieldT]):
    """
    Annotate empty Field ready to fill before first access

    Example:
        class Renderer:
            device = RequiredField(types=str)

        r = Renderer()
        r.device = "GPU"   # Valid
        print(r.device)    # "GPU"
        r.device = 123     # TypeError: expected str, got int
    """


@portlink(attach.LazyDescriptor)
class LazyField[T](WriteField, ReadField[T]):
    """
    Load and cache value on first read access

    Example:
        class Project:
            # Expensive calculation deferred until actually needed
            stats = LazyField(loader=lambda unit: unit._compute_stats())
    """

    def __init__(self, *args, loader: FieldLoader[T], **kwargs) -> None:
        self.loader: FieldLoader[T] = loader
        super().__init__(*args, **kwargs)

    def read(self, unit: object) -> T:
        if not self._has_val(unit):
            self.write(unit, value=self.loader(unit))
        return super().read(unit)


@portlink(attach.ReadDescriptor)
class DerivedField[T](ReadField[T]):
    """
    Calculate view on every access without maintaining state

    Example:
        class Window:
            width = RequiredField(types=int)
            height = RequiredField(types=int)

            # Recalculates every time it's called
            aspect_ratio = Derived(derived=lambda w: w.width / w.height)
    """

    def __init__(self, *args, calc: FieldLoader, **kwargs) -> None:
        self.derived: FieldLoader = calc
        self.__doc__: str | None = calc.__doc__
        self.public_name: str = funcname(calc)
        super().__init__(*args, **kwargs)

    def read(self, unit: object) -> T:
        return self.derived(unit)


@portlink(attach.ReadDescriptor)
class Forward[T](ReadField[T]):
    """
    Forward attribute from inner component

    Example:
        class Application:
            def __init__(self):
                self._bus = EventBus()

            # Expose the bus's emit method directly on the App
            emit = Forward(target="_bus", method="emit")
    """

    def __init__(
        self, target: str, method: str | None = None, /, *args, **kwargs
    ):
        self.target_name: str = target
        self.method_name: str | None = method
        super().__init__(*args, **kwargs)

    def __set_name__(self, owner: type, name: str) -> None:
        super().__set_name__(owner, name)
        if self.method_name is None:
            self.method_name = name

    def read(self, unit: object) -> T:
        target: Any = getattr(unit, self.target_name)
        return getattr(target, self.method_name or "")
