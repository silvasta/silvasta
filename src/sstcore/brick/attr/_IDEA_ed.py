"""
Class Attributes - Descripor

-
"""

from collections.abc import Callable
from typing import Any, overload

from sstcore.util.path import ProjectInfo


class Injected[T]:
    """Required instance attribute. No default. Set before first get."""

    def __init__(
        self, expected: type[T] | tuple[type, ...] | None = None
    ) -> None:
        self.expected = expected
        self.public_name = ""
        self.private_name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.private_name = f"_{name}"

    @overload
    def __get__(self, obj: None, owner: type) -> Injected[T]: ...
    @overload
    def __get__(self, obj: object, owner: type) -> T: ...

    def __get__(
        self, obj: object | None, owner: type | None = None
    ) -> T | Injected[T]:
        if obj is None:
            return self
        try:
            return obj.__dict__[self.private_name]
        except KeyError as exc:
            raise AttributeError(
                f"{type(obj).__name__}.{self.public_name} is not set"
            ) from exc

    def __set__(self, obj: object, value: T) -> None:
        if self.expected is not None and not isinstance(value, self.expected):
            raise TypeError(
                f"{type(obj).__name__}.{self.public_name} expected "
                f"{self.expected!r}, got {type(value).__name__}"
            )
        obj.__dict__[self.private_name] = value


class Collected[T]:
    """Lazy cached value. Factory runs once per instance on first get."""

    def __init__(self, factory: Callable[[Any], T]) -> None:
        self.factory = factory
        self.public_name = ""
        self.private_name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(
        self, obj: object | None, owner: type | None = None
    ) -> T | Collected[T]:
        if obj is None:
            return self
        data = obj.__dict__
        if self.private_name not in data:
            data[self.private_name] = self.factory(obj)
        return data[self.private_name]

    def __set__(self, obj: object, value: T) -> None:
        obj.__dict__[self.private_name] = value


class Derived[T]:
    """Computed view. No storage, no setter — subclasses may replace the descriptor."""

    def __init__(self, func: Callable[[Any], T]) -> None:
        self.func = func
        self.__doc__ = func.__doc__
        self.public_name = func.__name__

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name

    def __get__(
        self, obj: object | None, owner: type | None = None
    ) -> T | Derived[T]:
        if obj is None:
            return self
        return self.func(obj)


class Format(Derived[str]):
    # EXTRACT:
    def __init__(self, template: str) -> None:
        super().__init__(lambda obj, t=template: t.format(info=obj.info))


class PrinterInfo:
    info = Injected(ProjectInfo)
    project_info = Format("{info.name} v{info.version}")
