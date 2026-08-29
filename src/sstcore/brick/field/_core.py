"""
Class attribute Fields

- Attach with Descriptor
"""

__all__: list[str] = [
    "Injected",
    "Collected",
    "Derived",
    "Forward",
]

from typing import TYPE_CHECKING, Any

from ...port.attach import (
    FieldLoader,
    LazyDescriptor,
    ReadDescriptor,
    ValidDescriptor,
    WriteDescriptor,
)
from ..format import reflect
from ._base import ReadField, TypedField, WriteField


class Injected[T](ReadField[T], TypedField[T]):
    """
    TEXT

    Example:
        class Renderer:
            device = Injected(types=str)

        r = Renderer()
        r.device = "GPU"   # Valid
        print(r.device)    # "GPU"
        r.device = 123     # TypeError: expected str, got int
    """


class Collected[T](WriteField, ReadField[T]):
    """
    Prepare function for lazy loading

    Example:
        class Project:
            # Expensive calculation deferred until actually needed
            stats = Collected(loader=lambda unit: unit._compute_stats())
    """

    def __init__(self, *args, loader: FieldLoader, **kwargs) -> None:
        self.loader: FieldLoader = loader
        super().__init__(*args, **kwargs)

    def read(self, unit: object) -> T:
        if not self._has_val(unit):
            self.write(unit, value=self.loader(unit))
        return super().read(unit)


class Derived[T](ReadField[T]):
    """
    Recalculate view on every access without maintaining state

    Example:
        class Window:
            width = Injected(types=int)
            height = Injected(types=int)

            # Recalculates every time it's called
            aspect_ratio = Derived(derived=lambda w: w.width / w.height)
    """

    def __init__(self, *args, derived: FieldLoader, **kwargs) -> None:
        self.derived: FieldLoader = derived
        self.__doc__: str | None = derived.__doc__
        self.public_name: str = reflect.func(derived)
        super().__init__(*args, **kwargs)

    def read(self, unit: object) -> T:
        return self.derived(unit)


class Forward[T](ReadField[T]):
    """
    Forwards attribute access to an inner components

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

    def read(self, unit: object) -> T:
        target: object = getattr(unit, self.target_attr)
        return getattr(target, self.method_name)


if TYPE_CHECKING:
    _injected: type[WriteDescriptor] = Injected
    _injected: type[ValidDescriptor] = Injected
    _collected: type[LazyDescriptor[Any]] = Collected
    _derived: type[ReadDescriptor[Any]] = Derived
