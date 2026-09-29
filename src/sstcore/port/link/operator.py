"""
Operators - The mix

- temporary module
"""

import re
import typing as _t

from .___tree import MroTreeNode1, SubclassTreeNode, TypeTreeNode
from ._printer import printer
from .base import EasyAccessL1, EasyBase, EasyCatchL1, EasyCoreL1
from .data import mro_chain
from .define import DocMerger, Injecting, PortEmit, Reflecting


def main():
    # test_family_tree()
    test1_mro_tree()
    test2_mro_tree()
    test3_mro_tree()
    test4_type_tree()
    test5_type_tree()
    test6_mro_links()
    test7_mro_walk()
    test8_subclass()


class Easy[Core: _t.Callable](
    EasyCatchL1, EasyAccessL1, EasyCoreL1[Core], EasyBase
): ...


class LexicRegistry[Core: _t.Callable]:
    # class PortOperator[Core: _t.Callable](Easy):
    """Use class names as key"""

    port_emit: PortEmit
    # Nested registry: { CategoryBase: { "sub_id": SubClass } }
    _registry: dict[type, dict[str, type]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

        if cls.__name__.endswith("Base"):
            # Register the category base itself to hold children
            cls._registry[cls] = {}
            cls.port_emit(f"{cls.__name__}: Created Category...")
            return

        # Find the primary category parent in the MRO
        # It skips cls itself (index 0) and ignores Mixins that don't end in "Base"
        _category_parent = next(
            (
                b
                for b in cls.__mro__[1:]
                if issubclass(b, PortOperator) and b.__name__.endswith("Base")
            ),
            None,
        )

        if _category_parent:
            # Derive a simple ID relative to the parent
            local_id = cls.__name__.removeprefix(
                _category_parent.__name__.removesuffix("Base")
            ).lower()
            cls._registry[_category_parent][local_id] = cls
            cls.port_emit(
                f"{cls.__name__}: Registered under {_category_parent.__name__} as {local_id}"
            )


class CategorizedRegistry[Core: _t.Callable]:
    """Use parent as key"""

    port_emit: PortEmit
    _registry: dict[str, type[_t.Self]] = {}

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


class PortOperator[Core: _t.Callable](CategorizedRegistry, Easy): ...


# INFO: original
class _PortOperator[Core: _t.Callable](  # IMPORTANT: order!!
    EasyCatchL1,
    EasyAccessL1,
    EasyCoreL1[Core],
    EasyBase,
):
    """Mixed Base for all Easy Member"""

    _registry: dict[str, type[_t.Self]] = {}

    def __init_subclass__(cls, id: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if not id:
            cls.port_emit(f"{cls.__name__}: Ignored...")
        elif id in cls._registry:
            raise RuntimeError(f"Duplicated {cls}! [{id}]({cls._registry=})")
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


#  LINE: -- Processor -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ProcessorBase[Core](PortOperator):
    """Most likely independent of the others here..."""


#  LINE: -- Testing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def merger(source: str, target: str, /, joint: str = "") -> str:
    return f"""{source}{joint}{target}"""


def test_family_tree():
    with printer.topic("PortOperator"):
        _operator = PortOperator()
        printer.panel("PortOperator.Member")
        printer.lines(_operator._registry)

    with printer.topic("Processor"):
        proc: ProcessorBase[DocMerger] = ProcessorBase(
            state="running", core=merger
        )
        empty = proc((), ())
        printer.section("empty", empty)
        printer(proc)

    with printer.topic("Reflect"):
        reflect = _operator.spawn.reflect()
        printer.section("reflect", reflect)

    with printer.topic("Spawn"):
        Inject = _operator.spawn.inject  # noqa:N806
        printer(Inject.__mro__)
        inject = Inject(mode="soft", merge=merger)
        # TODO: inject = _operator.spown.injector(mode="soft", merge=merger)
        printer.section("inject", inject)
        printer.debug(inject)
        printer.header("MRO")


def test1_mro_tree():
    mro_tree = MroTreeNode1.build(ProcessorBase)
    printer.tree_graph(simple_tree=mro_tree, root="bold cyan", node="by_level")


def test2_mro_tree():
    mro_tree = MroTreeNode1.build(PortOperator)
    printer.tree_graph(simple_tree=mro_tree, root="bold cyan", node="by_level")


def test3_mro_tree():
    printer.mro_list_tree(InjectorBase)


def test4_type_tree():
    mro_tree = TypeTreeNode.from_bases(ReflectorBase)
    printer.tree_graph(simple_tree=mro_tree, root="bold cyan", node="by_level")


def test5_type_tree():
    printer.bases_to_rich(InjectorBase)


def test6_mro_links():
    mro_chain(InjectorBase)


def test7_mro_walk():
    printer.bases_tree(InjectorBase)


def test8_subclass():
    operator_tree = SubclassTreeNode.create(PortOperator)

    with printer.topic("PortOperator Subclass Hierarchy"):
        printer.tree_graph(operator_tree)


if __name__ == "__main__":
    main()
