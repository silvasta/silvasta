"""
Provide typed Data Transfer Objects for the EventBus

- CliDTO: Intended for __cli__ and processed by printer

"""

# LATER: move function implementations out of the port

__all__: list[str] = [
    "CliDTO",
]


import warnings
from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, Any, ClassVar, Self

if TYPE_CHECKING:
    from ...view import Renderable
from ._base import EventDTO


@dataclass
class CliDTO[ContentT: Renderable | list[Renderable]](EventDTO):
    content: ContentT

    style: str = "cyan"
    indent: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    _strict: ClassVar[bool] = False

    def __cli__(self) -> Self:
        return self

    @classmethod
    def from_call(cls, target: Any = None, **kwargs) -> Self:
        """Clean args and provide DTOs for all layout methods"""

        cleaned: dict[str, Any] = cls._clean_kwargs(kwargs)
        if target is not None:
            cleaned["content"] = target

        # TASK: clean this up!!
        # - remove redundancy and double check with _clean_kwargs
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
