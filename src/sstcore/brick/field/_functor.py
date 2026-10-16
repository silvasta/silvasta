"""
Mount the Functors as Fields

-
"""

import typing as _t
from typing import Any, Protocol

from ...port.attach import FieldLoader, ReadDescriptor
from ...port.functorial import Functorial
from ...port.link import portlink
from ._base import ReadField, ReadOnlyField


@portlink(ReadDescriptor)
class FunctorField[F: Functorial](ReadField[F], ReadOnlyField):
    """
    Declaratively mount a Functor to a host class as a read-only field.

    - Not a decorator (no `FieldDecorator` inheritance).
    - Non-writable at runtime and static check time (`NoWriteField`).
    - Instantiates the Functor lazily per host instance, forwarding host
      attributes specified in `host_attrs` to the Functor constructor.
    """

    def __init__(
        self,
        functor_cls: type[F],
        /,
        *host_attrs: str,
        **functor_kwargs: Any,
    ) -> None:
        # AI: this is much cleaner as the type[F]/F split below!
        self.functor_cls: type[F] = functor_cls
        self.host_attrs: tuple[str, ...] = host_attrs
        self.functor_kwargs: dict[str, Any] = functor_kwargs
        super().__init__(frozen=True)

    def _assemble(self, unit: object) -> F:
        return self.functor_cls(
            *(getattr(unit, attr) for attr in self.host_attrs),
            name=self.public_name,
            **self.functor_kwargs,
        )

    def read(self, unit: object) -> F:
        if not self._has_val(unit):
            mounted: F = self._assemble(unit)
            self._set_val(unit, mounted)
            return mounted
        return self._get_val(unit)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# MOVE: sstcore/port/functorial.py
class MountableFunctor[HostT](Functorial, _t.Protocol):
    @classmethod  # AI: this resolved issue in hasattr below, (unit was seen as self)
    def __mount__(cls, host: HostT, name: str) -> _t.Self:
        """Create or configure a functor instance bound to `host`."""

    def __init__(self, **kwargs): ...  # AI: for self.functor_target(name=)


class FunctorField3[F: MountableFunctor](ReadField[F], ReadOnlyField):
    """Mount Functor to Host class (read-only)"""

    def __init__(self, functor: type[F] | F, /, **kwargs: Any) -> None:
        self.functor_target: type[F] | F = functor
        self.mount_kwargs: dict[str, Any] = kwargs
        super().__init__(frozen=True)

    def __set_name__(self, owner: type, name: str) -> None:
        super().__set_name__(owner, name)
        if not isinstance(self.functor_target, type):
            self.functor_target.__name__ = name
            self.functor_target.__qualname__ = f"{owner.__qualname__}.{name}"

    def read(self, unit: object) -> F:
        if self._has_val(unit):
            return self._get_val(unit)
        if hasattr(self.functor_target, "__mount__"):
            # AI: the idea with __mount__ is amazing!
            # - the other ideas here add too much complexity for hypothetical usecases..
            # AI_TASK:
            # -> Combine this with the approach above
            mounted: F = self.functor_target.__mount__(
                unit, self.public_name, **self.mount_kwargs
            )
        elif isinstance(self.functor_target, type):
            mounted = self.functor_target(
                name=self.public_name, **self.mount_kwargs
            )
        else:
            return self.functor_target

        self._set_val(unit, mounted)

        return mounted


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FunctorDescriptor[F: Functorial](ReadDescriptor[F], Protocol):
    """Contract for read-only mounted Functor descriptors."""

    functor_cls: type[F]


@portlink(FunctorDescriptor)
class FunctorField2[Functor: Functorial](ReadField[Functor], ReadOnlyField):
    """
    Mount a Functor class declaratively as a read-only attribute.

    Instantiates lazily per host instance and caches in unit.__dict__.
    """

    def __init__(
        self,
        functor_cls: type[Functor],
        /,
        *init_attrs: str,
        **static_kwargs: Any,
    ) -> None:
        self.functor_cls: type[Functor] = functor_cls
        self.init_attrs: tuple[str, ...] = init_attrs
        self.static_kwargs: dict[str, Any] = static_kwargs
        super().__init__(frozen=True)

    def _build_functor(self, unit: object) -> Functor:
        return self.functor_cls(
            *(getattr(unit, attr) for attr in self.init_attrs),
            **(self.static_kwargs | {"name": self.public_name}),
        )

    def read(self, unit: object) -> Functor:
        if not self._has_val(unit):
            functor_instance: Functor = self._build_functor(unit)
            self._set_val(unit, functor_instance)
            return functor_instance
        return self._get_val(unit)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FunctorField1[F](ReadField[F], ReadOnlyField):
    """Mount one functor per instance.

    External ``__set__`` / ``__delete__`` always fail.
    Construction goes through ``_set_val`` so the lock is not the builder.
    """

    def __init__(
        self,
        producer: type[F],
        /,
        *inject: str,
        loader: FieldLoader[F] | None = None,
    ):
        if loader is None and not inject:
            raise TypeError(
                f"{producer.__name__}: pass injected attribute names or a loader"
            )
        self.producer: type[F] = producer
        self.inject: tuple[str, ...] = inject
        self.loader: FieldLoader[F] | None = loader
        super().__init__(frozen=True)

    def __set_name__(self, owner: type, name: str) -> None:
        super().__set_name__(owner, name)
        _inherited = getattr(owner, "__functor_fields__", {})
        owner.__functor_fields__ = {**_inherited, name: self}  # ty:ignore

    def build(self, unit: object) -> F:
        if self.loader is not None:
            built = self.loader(unit)
        else:
            built = self.producer(
                *(getattr(unit, attr) for attr in self.inject)
            )
        if not isinstance(built, self.producer):
            raise self.raiser.Function(
                self,
                unit,
                value=built,
                message="loader returned unexpected type",
            )
        return built

    def read(self, unit: object) -> F:
        if not self._has_val(unit):
            self._set_val(unit, self.build(unit))
        return self._get_val(unit)
