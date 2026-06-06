import random

from .nodes import SimpleTreeNode


def simple_tree():
    tree1 = SimpleTreeNode("tree1", branches=[], id="1")
    tree2 = SimpleTreeNode("tree2", branches=[], id="2")
    tree3 = SimpleTreeNode("tree3", branches=[], id="3")
    tree4 = SimpleTreeNode("tree4", branches=[], id="4")
    tree5 = SimpleTreeNode("tree5", branches=[], id="5")
    tree6 = SimpleTreeNode("tree6", branches=[], id="6")
    tree7 = SimpleTreeNode("tree7", branches=[], id="7")
    tree8 = SimpleTreeNode("tree8", branches=[], id="8")
    tree9 = SimpleTreeNode("tree9", branches=[], id="9")
    tree10 = SimpleTreeNode("tree10", branches=[], id="10")
    tree11 = SimpleTreeNode("tree11", branches=[], id="11")
    tree12 = SimpleTreeNode("tree12", branches=[], id="12")

    forest1 = SimpleTreeNode("forest1", branches=[tree1, tree2], id="13")
    forest2 = SimpleTreeNode(
        "forest2", branches=[tree3, tree4, tree5], id="14"
    )
    forest3 = SimpleTreeNode(
        "forest3", branches=[tree6, tree7, tree8], id="15"
    )
    forest4 = SimpleTreeNode(
        "forest4", branches=[tree9, tree10, tree11], id="16"
    )
    forest5 = SimpleTreeNode("forest5", branches=[tree12], id="17")

    biome = SimpleTreeNode(
        "biome",
        branches=[
            forest1,
            forest2,
            forest3,
            forest4,
            forest5,
        ],
        id="18",
    )
    return biome


def big_tree():
    """Random node generator for around 300 nodes (up to 700+)"""

    id: int = 0

    def branches_id() -> str:
        nonlocal id
        id += 1
        return str(id)

    return SimpleTreeNode(
        "biome",
        id=branches_id(),
        branches=[
            SimpleTreeNode(
                "forest",
                branches=[
                    SimpleTreeNode(
                        "tree",
                        branches=[
                            SimpleTreeNode(
                                "sprout", branches=[], id=branches_id()
                            )
                            for _sprout in range(random.randint(2, 12))
                        ],
                        id=branches_id(),
                    )
                    for _tree in range(random.randint(6, 8))
                ],
                id=branches_id(),
            )
            for _forest in range(random.randint(4, 8))
        ],
    )
