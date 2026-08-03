"""
Provide typed Data Transfer Objects for the EventBus

- CliDTO: Intended for __cli__ and processed by printer

"""

__all__: list[str] = [
    "CliDTO",
]

import warnings
from dataclasses import dataclass, field, fields
from typing import Any, ClassVar, Protocol, Self

from ._base import EventDTO

# LATER: move function implementation out of the port

# NEXT: content: Renderable


class _CliRenderable(Protocol):
    # NOTE: imitate definition in port.view
    def __cli__(self) -> CliDTO: ...


class _RichRenderable(Protocol):
    # NOTE: imitate definition in port.view
    def __rich__(self) -> _RichRenderable: ...


class _RichConsolable(Protocol):
    def __rich_console__(self): ...


# IMPORTANT: check with printer and view
type Renderable = _RichRenderable | _RichConsolable | _CliRenderable | str


@dataclass(kw_only=True)
class CliDTO(EventDTO):
    style: str = "cyan"
    indent: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    _strict: ClassVar[bool] = (
        False  # REMOVE: why ClassVar? maybe inside EventDTO?
    )
    _content_field: ClassVar[str] = "text"  # TODO: content:Renderable=""?

    def __cli__(self) -> Self:
        return self

    @classmethod
    def from_call(cls, target: Any = None, **kwargs) -> Self:
        """Clean args and provide DTOs for all layout methods"""

        cleaned: dict[str, Any] = cls._clean_kwargs(kwargs)
        if target is not None:
            cleaned[cls._content_field] = target

        try:
            instance: Self = cls(**cleaned)
            if instance.meta.get("unknown_args"):
                message = f"Unknown args: {instance.meta['unknown_args']}"
                if cls._strict:
                    raise TypeError(message)
                warnings.warn(message, stacklevel=2)
            return instance

        except TypeError as error:
            if cls._strict:
                raise
            cleaned.setdefault("meta", {})["error"] = str(error)
            return cls(
                **{k: v for k, v in cleaned.items() if k in cls._fields()}
            )

    @classmethod
    def _fields(cls) -> set[str]:
        return {field.name for field in fields(class_or_instance=cls)}

    @classmethod
    def _clean_kwargs(cls, kwargs: dict) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        valid_fields: set[str] = cls._fields()
        for key in list(kwargs.keys()):
            if key not in valid_fields:
                extra[key] = kwargs.pop(key)
        if extra:
            kwargs.setdefault("meta", {})["unknown_args"] = extra
        return kwargs
