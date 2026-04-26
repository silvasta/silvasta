import random
from collections import defaultdict, deque
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self


@dataclass(frozen=True)
class SimpleTreeNode:
    name: str
    id: str | None = None
    branches: Sequence[Self] = field(default_factory=list)

    @property
    def display_label(self) -> str:
        return self.name

    @property
    def identifier(self):
        return self.id


@dataclass(frozen=True)
class PathTreeNode(SimpleTreeNode):
    path: Path = field(default_factory=Path)

    @property
    def identifier(self):
        return self.path

    @classmethod
    def create(
        cls, path: Path, branches: Sequence[Self] | None = None
    ) -> Self:
        if branches is None:
            branches: Sequence[Self] = []

        return cls(name=path.name, path=path, branches=branches)


def build_path_tree(paths: list[Path], root_name: str = "") -> PathTreeNode:
    """Build Tree from raw paths with stacked nodes at empty directories"""

    path_parts: list[deque[str]] = [deque(path.parts) for path in paths]

    return recursive_tree(path_parts, current_node_name=root_name)


def pop_left(path_parts: list[deque]) -> dict[str, list[deque]]:
    """Squash all top left path elements into branched dict, filter empty path path segments,
    returns dict with 1-n keys each with list of 0-k shortened deque elements"""

    current_nodes: dict[str, list[deque]] = defaultdict(list)

    for path_queue in path_parts:
        if len(path_queue) == 0:
            continue
        path_segment: str = path_queue.popleft()
        current_nodes[path_segment].append(path_queue)

    return current_nodes


def recursive_tree(
    path_parts: list[deque[str]],
    current_node_name: str = "",
    current_node_path: Path = Path(),
) -> PathTreeNode:

    branches: dict[str, list[deque[str]]] = pop_left(path_parts)
    branches_nodes: list[PathTreeNode] = []

    for name, branches_path_parts in branches.items():
        path: Path = current_node_path / name

        if len(branches) == 1:
            if len(branches_path_parts) == 0:
                return PathTreeNode(name=name, path=path)

            # Stack names to avoid unnecessary Nodes
            if current_node_name == "/":
                branches_name: str = f"/{name}"
            elif current_node_name:
                branches_name: str = f"{current_node_name}/{name}"
            else:
                branches_name: str = name

            return recursive_tree(
                path_parts=branches_path_parts,
                current_node_name=branches_name,
                current_node_path=path,
            )
        branches_nodes.append(
            recursive_tree(
                path_parts=branches_path_parts,
                current_node_name=name,
                current_node_path=path,
            )
        )
    return PathTreeNode(
        name=current_node_name,
        path=current_node_path,
        branches=branches_nodes,
    )


def get_example_tree():
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


def get_big_example_tree():
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
