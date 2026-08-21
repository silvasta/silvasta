"""
Update the internal Error

- Pipeline inbetween DependencyLevel[0-2]

"""

from ...port.error import Error
from ._reflect import cls_name


class FormatError(Error):
    """Attach Normalizer?"""

    @property
    def name(self) -> str:
        """Format the Name of the Exception"""
        return cls_name(target=self)
