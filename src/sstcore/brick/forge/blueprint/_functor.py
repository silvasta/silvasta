"""
Shape the Blueprint for Toolkits equipped with Static Functions

FunctorMeta
  - auto-convert public methods in class body to staticmethod
  - attach customizable views with defaults


"""

__all__: list[str] = [
    "FunctorMeta",
    "FunctorMetaData",
]


from typing import TYPE_CHECKING, Any

from ....port.color import Color, ColorIdentifier
from ....port.shape import Meta, MetaData
from ...color._arg import resolve_color


class FunctorMeta(type):
    """Create Blueprint for Active Functorials"""

    _data: FunctorMetaData

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: FunctorMetaData | None = None,
    ):
        """Attach all methods as staticmethod and load input for dunder data"""

        # IDEAS: what to modify in namespace?
        # INFO: below, from StaticFuncMeta
        # new_static_methods: dict[str, Any] = {
        #     key: staticmethod(value)
        #     for key, value in namespace.items()
        #     if not key.startswith("_") and isinstance(value, FunctionType) }
        # namespace.update(new_static_methods)

        cls = super().__new__(mcls, name, bases, namespace)

        cls._data = data or FunctorMetaData()

        return cls

    def __call__(cls, *_, **__) -> Any: ...

    # IDEA: what to show for Functor?
    # INFO: below, from StaticFuncMeta:
    # def toolkit(cls, sort: bool = True) -> list[str]:
    #     """Provide names of all public staticmethods"""
    #     names: list[str] = [
    #         name
    #         for name in dir(cls)
    #         if not name.startswith("_")
    #         and isinstance(inspect.getattr_static(cls, name), staticmethod) ]
    #     return sorted(names) if sort else names


class FunctorMetaData:
    """InputSpace, Defaults, Pre-processing -> finally data container"""

    # IDEAS:
    # - views?
    # - the func?
    # - policy?

    def __init__(self, color: ColorIdentifier = Color.AZURE):
        # TODO:
        self.color: Color = resolve_color(color_guess=color)

    def _default_xxx(self) -> Any:
        raise NotImplementedError


if TYPE_CHECKING:
    _cls_meta: type[Meta] = FunctorMeta
    _cls_data: type[MetaData] = FunctorMetaData
    _instance_data: MetaData = FunctorMetaData()
