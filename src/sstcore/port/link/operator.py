"""
Operators - The mix

- temporary module
"""

import typing as _t

from ._error import LinkRaiser
from .base import EasyAccessL1, EasyBase, EasyCatchL1, EasyCoreL1
from .define import Injecting, Reflecting


class Easy[Core: _t.Callable](  # IMPORTANT: order!!
    EasyCatchL1,
    EasyAccessL1,
    EasyCoreL1[Core],
    EasyBase,
): ...


class PortOperator[Core: _t.Callable](Easy[Core]):
    """Mixed Base for all Easy Member"""

    _registry: dict[str, type[_t.Self]] = {}

    def __init_subclass__(cls, id: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if not id:
            cls.port_emit(f"{cls.__name__}: Ignored...")
        elif id in cls._registry:
            raise LinkRaiser.PipeLine(
                f"Duplicated {cls}[{id}]", id=id, state=cls._registry
            )

        else:
            cls._registry[id] = cls
            cls.port_emit(f"{cls.__name__}: Registered: {id}")

    @property
    def spawn(self) -> Spawner:
        return Spawner(registry=self._registry)


class Spawner[T: type]:  # TODO: proper types, final Reflect,Inject and Collect
    """Provide extended access for presets"""

    operators: frozenset[str] = frozenset({"reflect", "collect", "inject"})

    def __init__(self, registry: dict[str, T]):
        if missing := self.operators - registry.keys():
            raise RuntimeError(f"Missing Operators! [{missing}]({registry=})")
        self._registry: dict[str, T] = registry

    @property
    def reflect(self) -> T:
        return self._registry["reflect"]

    @property
    def collect(self) -> T:
        return self._registry["collect"]

    @property
    def inject(self) -> T:
        return self._registry["inject"]


#  LINE: -- Pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ReflectorBase(PortOperator[Reflecting]):
    """Collect the Detecting and Extracting Methods"""


class InjectorBase(PortOperator[Injecting]):
    """Collect the Modificating Methods with Safety"""


class CollectorBase[Core: _t.Callable](PortOperator[Core]):
    """Run the MRO pipelines and Reflect and Inject data"""
