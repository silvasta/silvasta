from dataclasses import asdict, dataclass, fields, is_dataclass
from typing import Any, Self, dataclass_transform

from sstcore.brick.call import ArgCast
from sstcore.brick.call._cast import apply_mapping

TEST = 1


# port/spec.py
@dataclass_transform(kw_only_default=True)
class SpecBase:
    def __init_subclass__(cls, kw_only: bool = True, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        dataclass(kw_only=kw_only, **kwargs)(cls)

    @classmethod
    def absorb(cls, kwargs: dict[str, Any]) -> Self:
        packed = cls.pack(kwargs)
        return cls(**pluck(packed, cls, consume=True))

    @classmethod
    def pack(cls, kwargs: dict[str, Any]) -> dict[str, Any]:
        return kwargs


def field_names(cls: type) -> set[str]:
    return {f.name for f in fields(cls)}


def pluck(data: dict[str, Any], cls: type, *, consume: bool) -> dict[str, Any]:
    names = field_names(cls)
    if consume:
        return {key: data.pop(key) for key in list(data) if key in names}
    return {key: data[key] for key in names & data.keys()}


def project[T](spec: Any, target: type[T]) -> T:
    return target(**{f.name: getattr(spec, f.name) for f in fields(target)})


def merge_asdict(*parts: Any) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for part in parts:
        merged.update(asdict(part) if is_dataclass(part) else dict(part))
    return merged


@classmethod
def absorb(cls, kwargs: dict[str, Any], *, cast: bool = False) -> Self:
    packed = cls.pack(kwargs)
    if cast:
        apply_mapping(ArgCast.walk_plan(cls), packed)
    return cls(**pluck(packed, cls, consume=True))
