"""
Collect Callables ready to assembe on Calling Objects

                                   DependencyLevel.sstcore.brick[1]
"""

__all__: list[str] = [
    "StackBase",
    "StackLayer",
    "StackCore",
    "StackState",
    "StackRunner",
    # examples
    "ANSI_STACK",
    "DTO_STACK",
    "STRING_STACK",
]

from ._core import StackBase, StackCore, StackLayer, StackRunner, StackState
from ._example import ANSI_STACK, DTO_STACK, STRING_STACK

# IDEA: from ._core import StackCore -> assemble Stub data here
# maybe as a general pattern:
# package_root/
# - __init__.py
# - __init__.pyi
# - *.py
# - _write.py as general target point to hook in
# - _stub/*.pyi in case separated sorting is needed
