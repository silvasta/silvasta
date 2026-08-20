"""
Update the internal Error

- Pipeline inbetween DependencyLevel[0-2]

"""

from ...port.error import BaseError
from ..format import cls_name


class Error(BaseError):  # IMPORTANT: check intermediate Error steps
    @property
    def name(self) -> str:
        """Provide ClassName ( __str__ already used for message builtins.Exception"""
        return cls_name(target=self)
