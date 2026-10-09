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
from typing import Any

from ....brick.color.box import Colors
from ....port.link import portlink
from ....port.shape import Meta, MetaData
from ._meta_view import ClsViewBase, ClsViewData

colors = Colors()


@portlink(MetaData)
class StaticFuncMetaData(ClsViewData):  # IDEAS: - some toolkit config
    """Collect views and ..."""


@portlink(Meta)
class StaticFuncMeta(ClsViewBase):
    """Create Blueprint for Static Functorials"""

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: StaticFuncMetaData,
    ):
        """Attach all methods as staticmethod and load input for dunder data"""

        # EXTRACT: auto-staticmethods, add config for _private,...
        new_static_methods: dict[str, Any] = {
            key: staticmethod(value)
            for key, value in namespace.items()
            if not key.startswith("_") and isinstance(value, FunctionType)
        }
        namespace.update(new_static_methods)

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
