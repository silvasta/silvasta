"""
IDEA: assemble the errors here with full brick support and no internal deps

-
"""

from ..port.error import SstError


class ViewError(SstError):  # TODO: view error
    # IMPORTANT: already used
    """Explain what forge.view failed"""


class FuncError(SstError):  # TODO: check
    """Explain what forge.func failed"""


class BuildError(SstError):  # TODO: check
    """Explain what forge.build failed"""
