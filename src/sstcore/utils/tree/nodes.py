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

    return _recursive_path_tree(path_parts, current_node_name=root_name)


def _recursive_path_tree(
    path_parts: list[deque[str]],
    current_node_name: str = "",
    current_node_path: Path = Path(),
) -> PathTreeNode:

    branches: dict[str, list[deque[str]]] = _pop_left(path_parts)
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

            return _recursive_path_tree(
                path_parts=branches_path_parts,
                current_node_name=branches_name,
                current_node_path=path,
            )
        branches_nodes.append(
            _recursive_path_tree(
                path_parts=branches_path_parts,
                current_node_name=name,
                current_node_path=path,
            )
        )
    return PathTreeNode(
        name=current_node_name,
        path=current_node_path,
        branches=branches_nodes,  # TODO: sort!?
    )


def _pop_left(path_parts: list[deque]) -> dict[str, list[deque]]:
    """Squash all top left path elements into branched dict.

    Filter empty path path segments, shorten remaining deque element,
    and provide dict with 1-n keys each with list of 0-k"""

    current_nodes: dict[str, list[deque]] = defaultdict(list)

    for path_queue in path_parts:
        if len(path_queue) == 0:
            continue
        path_segment: str = path_queue.popleft()
        current_nodes[path_segment].append(path_queue)

    return current_nodes
