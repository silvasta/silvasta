import re
from collections.abc import Callable
from typing import Self

from ...port._raise import LinkRaiser
from ...port.link._operator import PortOperator

type _PortEmit = Callable


class SpawnOperator[Core: Callable]:
    """Mixed Base for all Easy Member"""

    port_emit: _PortEmit
    _registry: dict[str, type[Self]] = {}

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


class LexicRegistry[Core: Callable]:
    # class SpawnOperator[Core: Callable](Easy):
    """Nested registry: { CategoryBase: { "sub_id": SubClass } }"""

    port_emit: _PortEmit
    _registry: dict[type, dict[str, type]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

        if cls.__name__.endswith("Base"):
            cls._registry[cls] = {}
            cls.port_emit(f"{cls.__name__}: Created Category...")
            return

        def _check(b) -> bool:
            return issubclass(b, PortOperator) and b.__name__.endswith("Base")

        if _category_parent := next(
            (b for b in cls.__mro__[1:] if _check(b)), None
        ):
            local_id = cls.__name__.removeprefix(
                _category_parent.__name__.removesuffix("Base")
            ).lower()
            cls._registry[_category_parent][local_id] = cls
            cls.port_emit(
                f"{cls.__name__}: Registered under {_category_parent.__name__} as {local_id}"
            )


# EXTRACT: to some __init_subclass__ module?
class CategorizedRegistry[Core: Callable]:
    # EXTRACT: to some __init_subclass__ module?
    """Use parent as key and build Tree like family"""

    port_emit: _PortEmit
    _registry: dict[str, type[Self]] = {}

    def __init_subclass__(cls, id: str = "", abstract: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)

        if abstract or cls.__name__.endswith("Base"):
            cls.port_emit(f"{cls.__name__}: Ignored...")
            return

        if not id:
            id = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

        if id in cls._registry:
            raise RuntimeError(f"Duplicated {cls}! [{id}]({cls._registry=})")

        cls._registry[id] = cls
        cls.port_emit(f"{cls.__name__}: Registered: {id}")
