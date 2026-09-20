"""
Assemble the first level of composed Fields

Prepare for direct Usage and as Base for further Specicications

- RequiredField: placeholder for dynamic typed value attach
- LazyField: placeholder with zero arg factory
- DerivedField: calculate with dynamic attributes
- Forward: direct access to inner attributes, Outer.access = Outer.Inner.access

                                                 DependencyLevel[2]
"""

__all__: list[str] = [
    "RequiredField",
    "LazyField",
    "DerivedField",
    "Forward",
]

from typing import TYPE_CHECKING, Any

from ...port import attach
from ...port.attach import FieldLoader
from ..labor import reflect
from ._base import ReadField, WriteField
from ._extend import TypedField


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


# NEXT:
class DerivedField[T](ReadField[T]):
    # IDEA:: derive or combine with DecoratedField??
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
        self.public_name: str = reflect.func(calc)
        super().__init__(*args, **kwargs)

    def read(self, unit: object) -> T:
        return self.derived(unit)


class Forward[T](ReadField[T]):  # NOTE: this name is perfect
    """
    Forward attribute from inner component

    Example:
        class Application:
            def __init__(self):
                self._bus = EventBus()

            # Expose the bus's emit method directly on the App
            emit = Forward(target_attr="_bus", method_name="emit")
    """

    def __init__(self, target_attr: str, method_name: str):
        self.target_attr: str = target_attr
        self.method_name: str = method_name
        # WARN: forward by super here or not??

    def read(self, unit: object) -> T:
        target: object = getattr(unit, self.target_attr)
        return getattr(target, self.method_name)


if TYPE_CHECKING:
    _collected: type[attach.LazyDescriptor[Any]] = LazyField
    _collected: type[attach.ReadDescriptor] = LazyField
    _collected: type[attach.WriteDescriptor] = LazyField
    _derived: type[attach.ReadDescriptor[Any]] = DerivedField
    _forwarded: type[attach.ReadDescriptor[Any]] = Forward
    _injected: type[attach.WriteDescriptor] = RequiredField
    _injected: type[attach.ValidDescriptor] = RequiredField
