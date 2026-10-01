"""
IDEA: assemble the errors here with full brick support and no internal deps

-
"""

from ..port.raising import SstCoreError

# TASK: Raiser


class ViewError(SstCoreError):  # TODO: view error
    """Explain what forge.view failed"""


class FuncError(SstCoreError):  # TODO: check
    """Explain what forge.func failed"""


class BuildError(SstCoreError):  # TODO: check
    """Explain what forge.build failed"""
