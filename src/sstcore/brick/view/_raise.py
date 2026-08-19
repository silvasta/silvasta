"""
Update the internal Error

- Pipeline inbetween DependencyLevel[0-2]

"""

from ...port.error import BaseError
from ..format import cls_name


# IMPORTANT: check intermediate Error steps
class Error(BaseError):
    @property
    def name(self) -> str:
        """Provide ClassName ( __str__ already used for message builtins.Exception"""
        return cls_name(target=self)
