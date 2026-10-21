"""
Mount the Functors as Fields

-
"""

__all__: list[str] = [
    "FunctorField",
]


from typing import Any

from ...port.attach import ReadDescriptor
from ...port.functorial import MountableFunctor
from ...port.link import portlink
from ._base import ReadField, ReadOnlyField


@portlink(ReadDescriptor)
class FunctorField[F: MountableFunctor](ReadField[F], ReadOnlyField):
    """
    Declaratively mount a Functor class to a host class as a read-only field

    - Non-decorator, read-only data descriptor (`ReadField` + `ReadOnlyField`).
    - Instantiates the Functor lazily per host instance via `F.__mount__`
      and caches it in `unit.__dict__`.
    """

    def __init__(self, functor_cls: type[F], /, **mount_kwargs: Any) -> None:
        self.functor_cls: type[F] = functor_cls
        self.mount_kwargs: dict[str, Any] = mount_kwargs
        super().__init__(frozen=True)

    def _assemble(self, unit: object) -> F:
        return self.functor_cls.__mount__(
            unit, name=self.public_name, **self.mount_kwargs
        )

    def read(self, unit: object) -> F:
        if not self._has_val(unit):
            mounted: F = self._assemble(unit)
            self._set_val(unit, mounted)
            return mounted
        return self._get_val(unit)
