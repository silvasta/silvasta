from silvasta.utils import printer
from silvasta.utils.simple_tree import SimpleTreeNode, get_example_tree

printer.title("Print the SimpleTree", title="SimpleTree")

example_tree: SimpleTreeNode = get_example_tree()

printer.tree_graph(example_tree)
