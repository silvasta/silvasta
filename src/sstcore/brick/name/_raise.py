"""
Update the internal Error

- Pipeline inbetween DependencyLevel[0-2]

"""

from ..color._raise import ColorError


class PatternError(ColorError):
    """Attach ColoredName that builds __rich__ from name"""
