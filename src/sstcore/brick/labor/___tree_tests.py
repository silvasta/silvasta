"""
Class Registry

- Spawn SubClasses from BaseClass

"""

from typing import Protocol

from ...port.link._model import (
    Docs,
    PlugDoc,
    PortDoc,
    PortLinkData,
    PortLinkDocs,
    PortLinks,
    SidePolicy,
)
from ...port.link._operator import Inject, PortOperator, Reflect
from ...port.link._render import printer
from .___tree_dto_printy import (
    MroTreeNode1,
    MroTreeNode2,
    SubclassTreeNode,
    TypeTreeNode,
)

# NEXT: move to util.tree! most
# NEXT: move to util.tree! most
# NEXT: move to util.tree! most


def main():
    _edit_and_save()
    mro_chain(Inject)
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
    mro_tree = MroTreeNode1.build(Reflect)
    printer.tree_graph(simple_tree=mro_tree, root="bold cyan", node="by_level")


def test2_mro_tree():
    mro_tree = MroTreeNode1.build(PortOperator)
    printer.tree_graph(simple_tree=mro_tree, root="bold cyan", node="by_level")


def test3_mro_tree():
    printer.mro_list_tree(Inject)


def test4_type_tree():
    mro_tree = TypeTreeNode.from_bases(Reflect)
    printer.tree_graph(simple_tree=mro_tree, root="bold cyan", node="by_level")


def test5_type_tree():
    printer.bases_to_rich(Inject)


def test6_mro_links():
    mro_chain(Inject)


def test7_mro_walk():
    printer.bases_tree(Inject)


def test8_subclass():
    operator_tree = SubclassTreeNode.create(PortOperator)

    with printer.topic("PortOperator Subclass Hierarchy"):
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
            printer(f"{doc} -> {policy.name}: {policy.valid(doc)}")  # ty:ignore


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
    with printer.topic("PortOperator"):
        _operator = PortOperator()
        printer.panel("PortOperator.Member")
        printer.lines(_operator._registry)

    with printer.topic("Processor"):
        proc: Reflect = Reflect(state="running", core=merger)
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
