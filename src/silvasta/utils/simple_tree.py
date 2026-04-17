import random
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
    tree1 = SimpleTreeNode("tree1", next=[], id="1")
    tree2 = SimpleTreeNode("tree2", next=[], id="2")
    tree3 = SimpleTreeNode("tree3", next=[], id="3")
    tree4 = SimpleTreeNode("tree4", next=[], id="4")
    tree5 = SimpleTreeNode("tree5", next=[], id="5")
    tree6 = SimpleTreeNode("tree6", next=[], id="6")
    tree7 = SimpleTreeNode("tree7", next=[], id="7")
    tree8 = SimpleTreeNode("tree8", next=[], id="8")
    tree9 = SimpleTreeNode("tree9", next=[], id="9")
    tree10 = SimpleTreeNode("tree10", next=[], id="10")
    tree11 = SimpleTreeNode("tree11", next=[], id="11")
    tree12 = SimpleTreeNode("tree12", next=[], id="12")

    forest1 = SimpleTreeNode("forest1", next=[tree1, tree2], id="13")
    forest2 = SimpleTreeNode("forest2", next=[tree3, tree4, tree5], id="14")
    forest3 = SimpleTreeNode("forest3", next=[tree6, tree7, tree8], id="15")
    forest4 = SimpleTreeNode("forest4", next=[tree9, tree10, tree11], id="16")
    forest5 = SimpleTreeNode("forest5", next=[tree12], id="17")

    biome = SimpleTreeNode(
        "biome",
        next=[
            forest1,
            forest2,
            forest3,
            forest4,
            forest5,
        ],
        id="18",
    )
    return biome


def get_big_example_tree():

    id: int = 0

    def next_id() -> str:
        nonlocal id
        id += 1
        return str(id)

    return SimpleTreeNode(
        "biome",
        id=next_id(),
        next=[
            SimpleTreeNode(
                "forest",
                next=[
                    SimpleTreeNode(
                        "tree",
                        next=[
                            SimpleTreeNode("sprout", next=[], id=next_id())
                            for _sprout in range(random.randint(2, 12))
                        ],
                        id=next_id(),
                    )
                    for _tree in range(random.randint(6, 8))
                ],
                id=next_id(),
            )
            for _forest in range(random.randint(4, 8))
        ],
    )
