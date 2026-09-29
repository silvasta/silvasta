"""
Class Registry

- Spawn SubClasses from BaseClass

"""

import re
from collections.abc import Callable
from types import SimpleNamespace
from typing import Protocol, Self

from ....brick.labor.mro.___mrotree import (
    MroTreeNode1,
    MroTreeNode2,
    SubclassTreeNode,
    TypeTreeNode,
)
from ....port.link._error import LinkRaiser
from ....port.link._printer import printer
from ....port.link.data import (
    Docs,
    PlugDoc,
    PortDoc,
    PortLinkData,
    PortLinkDocs,
    PortLinks,
    SidePolicy,
)


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
            return issubclass(b, Operator) and b.__name__.endswith("Base")

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


class CategorizedRegistry[Core: Callable]:
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


class _PortEmit[**P](Protocol):
    def __call__(self, *arg: P.args, **kwarg: P.kwargs) -> None: ...


class Operator: ...


class ReflectorBase(Operator):
    """Collect the Detecting and Extracting Methods"""


class InjectorBase(Operator):
    """Collect the Modificating Methods with Safety"""


class CollectorBase[Core: Callable]:
    """Run the MRO pipelines and Reflect and Inject data"""


#  LINE: -- Processor -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ProcessorBase[Core](Operator, SimpleNamespace):
    """Most likely independent of the others here..."""


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def main():
    _edit_and_save()
    mro_chain(ProcessorBase)
    # test_family_tree()
    test1_mro_tree()
    test2_mro_tree()
    test3_mro_tree()
    test4_type_tree()
    test5_type_tree()
    test6_mro_links()
    test7_mro_walk()
    test8_subclass()


def test1_mro_tree():
    mro_tree = MroTreeNode1.build(ProcessorBase)
    printer.tree_graph(simple_tree=mro_tree, root="bold cyan", node="by_level")


def test2_mro_tree():
    mro_tree = MroTreeNode1.build(Operator)
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
    operator_tree = SubclassTreeNode.create(Operator)

    with printer.topic("Operator Subclass Hierarchy"):
        printer.tree_graph(operator_tree)


def _edit_and_save():
    class _Merging(Protocol): ...

    Merge = type("Merge", (object,), {})  # noqa:N806
    docs: Docs = (
        PortDoc("proto desc", "extract", source=_Merging),
        PortDoc("proto", "format", source=_Merging),
        PlugDoc("impl", "format", source=Merge),
    )

    with printer.topic("Transfom PortLinkData"):
        docs_frozen = PortLinkDocs(docs)
        printer.repr(docs_frozen)
        printer.line()

        docs_active: PortLinks = docs_frozen.edit()
        printer.repr(docs_active)
        docs_active.fill(PortDoc("test", "attr1", _Merging))
        docs_active.fill(PlugDoc("test2", "attr2", Merge))
        printer.repr(docs_active)
        printer.line()

        final_docs: PortLinkDocs = docs_active.save()
        printer.repr(final_docs)
        printer(f"{final_docs.attrs=}")
        printer(f"{final_docs.sources=}")

    with printer.topic("Policy"):
        from itertools import product

        for doc, policy in list(product(docs, SidePolicy)):
            printer(f"{doc} -> {policy.name}: {policy.valid(doc)}")


def mro_chain(
    cls: type,
    links: PortLinkData | None = None,
    *,
    skip: frozenset[type] = frozenset({object}),
) -> MroTreeNode2:
    rows = [
        (index, base)
        for index, base in enumerate(cls.__mro__)
        if base not in skip
    ]
    node: MroTreeNode2 | None = None
    for index, base in reversed(rows):
        node = MroTreeNode2(
            cls=base, mro_index=index, branches=(node,) if node else ()
        )
        if links is not None and base in links:
            # display only; merge still uses __mro__ order, not this tree
            _ = links[base]
    if node is None:
        raise ValueError(cls)
    printer(node)
    return node


def merger(source: str, target: str, /, joint: str = "") -> str:
    return f"""{source}{joint}{target}"""


def test_family_tree():
    with printer.topic("Operator"):
        _operator = SpawnOperator()
        printer.panel("Operator.Member")
        printer.lines(_operator._registry)

    with printer.topic("Processor"):
        proc: ProcessorBase = ProcessorBase(state="running", core=merger)
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


if __name__ == "__main__":
    main()
