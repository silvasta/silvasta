from dataclasses import dataclass, field
from typing import Self


@dataclass(frozen=True)
class SimpleTreeNode:
    name: str
    id: str | None = None
    next: list[Self] = field(default_factory=list)


def snapshot_pydantic_tree(pydantic_node) -> SimpleTreeNode:
    # MOVE: data or Project

    # 1. Extract what you need from the heavy model
    node_name = pydantic_node.title_or_name_or_whatever

    # 2. Recursively snapshot the children
    simple_children = [
        snapshot_pydantic_tree(child) for child in pydantic_node.children
    ]

    # 3. Return the lightweight dataclass
    return SimpleTreeNode(name=node_name, next=simple_children)


def get_example_tree():
    tree1 = SimpleTreeNode("tree1", next=[])
    tree2 = SimpleTreeNode("tree2", next=[])
    tree3 = SimpleTreeNode("tree3", next=[])
    tree4 = SimpleTreeNode("tree4", next=[])
    tree5 = SimpleTreeNode("tree5", next=[])
    tree6 = SimpleTreeNode("tree6", next=[])
    tree7 = SimpleTreeNode("tree7", next=[])
    tree8 = SimpleTreeNode("tree8", next=[])
    tree9 = SimpleTreeNode("tree9", next=[])
    tree10 = SimpleTreeNode("tree10", next=[])
    tree11 = SimpleTreeNode("tree11", next=[])
    tree12 = SimpleTreeNode("tree12", next=[])

    forest1 = SimpleTreeNode("forest1", next=[tree1, tree2])
    forest2 = SimpleTreeNode("forest2", next=[tree3, tree4, tree5])
    forest3 = SimpleTreeNode("forest3", next=[tree6, tree7, tree8])
    forest4 = SimpleTreeNode("forest4", next=[tree9, tree10, tree11])
    forest5 = SimpleTreeNode("forest5", next=[tree12])

    biome = SimpleTreeNode(
        "biome",
        next=[
            forest1,
            forest2,
            forest3,
            forest4,
            forest5,
        ],
    )
    return biome
