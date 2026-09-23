"""
Shape the Blueprint for Toolkits equipped with Static Functions

StaticFuncMeta
  - auto-convert public methods in class body to staticmethod
  - attach customizable views with defaults

"""

__all__: list[str] = [
    "StaticFuncMeta",
    "StaticFuncMetaData",
]


import inspect
from types import FunctionType
from typing import TYPE_CHECKING, Any

from ....brick.color.box import Colors
from ....port.color import ColorBox
from ....port.shape import Meta, MetaData
from ._base import MetaViewBase, MetaViewData

colors: ColorBox = Colors()  # ty:ignore


class StaticFuncMetaData(MetaViewData):
    # IDEAS:
    # - some toolkit config
    # - namespace policy: FunctionType or what else? some selection
    """Collect views and ..."""


class StaticFuncMeta(MetaViewBase):
    """Create Blueprint for Static Functorials"""

    _data_class = StaticFuncMetaData
    # TASK: find better way for default cls
    _data: StaticFuncMetaData

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: StaticFuncMetaData | None = None,  # IDEA: not optional?
    ):
        """Attach all methods as staticmethod and load input for dunder data"""

        new_static_methods: dict[str, Any] = {
            key: staticmethod(value)
            for key, value in namespace.items()
            if not key.startswith("_") and isinstance(value, FunctionType)
        }
        namespace.update(new_static_methods)

        # TASK: how to handle this: cls._data = data or StaticFuncMetaData()
        return super().__new__(mcls, name, bases, namespace, data=data)

    def __call__(cls, *_, **__) -> Any:  # noqa:N805
        raise TypeError(f"StaticFunc[{cls}] is Not available as Instance!")

    def toolkit(cls, sort: bool = True) -> list[str]:  # noqa:N805
        """Provide names of all public staticmethods"""

        # TODO: candidate for format.reflect
        # Parameter:
        # - public/private
        # - {static|class}method|property, what else?

        names: list[str] = [
            name
            for name in dir(cls)
            if not name.startswith("_")
            and isinstance(inspect.getattr_static(cls, name), staticmethod)
        ]
        return sorted(names) if sort else names


if TYPE_CHECKING:
    _cls_meta: type[Meta] = StaticFuncMeta
    _cls_data: type[MetaData] = StaticFuncMetaData
    _instance_data: MetaData = StaticFuncMetaData()
