"""
Inspect arbitrary objects and safely pull out specific attributes

                                                           ModuleLevel[0]
"""

__all__: list[str] = [  # NEXT: module name??
    "clsname",
    "data",
    "pydatic",
    "_dict",
]


from typing import Any

from ....port.calling import PydanticModel


def clsname(_target: Any) -> str:
    # IDEA: reflect.cls then reflect.cls.ancestor|sort|...
    # TODO: single? yes but as well in combo,
    # maybe with heavily improvements? check eg _mro
    """Extract name from instance or class"""
    return getattr(_target, "__name__", type(_target).__name__)


def data(_target: Any, exclude: set[str] | None = None) -> dict[str, Any]:
    # TODO: public/privat, other param, small toolbox
    """Extract public attributes filtered by exclude"""
    return {
        k: v
        for k, v in vars(_target).items()
        if not k.startswith("_") and k not in (exclude or set())
    }


def pydatic(
    _target: Any, *, exclude: set[str] | None = None
) -> dict[str, Any]:
    # TODO: extension of data
    """Extract public Pydantic attributes filtered by exclude"""

    exclude: set[str] = exclude or set()

    if isinstance(_target, PydanticModel):
        return _target.model_dump(exclude=exclude)

    return data(_target, exclude)


def _dict(_target: Any, *, key: str) -> Any:
    # IDEA: acces : reflect.cls.dict
    """Direct __dict__ access"""
    return _target.__dict__[key]
