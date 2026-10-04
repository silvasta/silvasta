from .._base import BaseField


class _IdeaFieldAccess(BaseField):
    """Provide a helper Mixin?"""

    @property
    def can_reset(self) -> bool:
        return False

    @property
    def can_load(self) -> bool:  # CHECK: if not redundant
        return False

    def is_readable(self, unit) -> bool:
        return self.can_load or self._has_val(unit)

    def is_writable(self, unit) -> bool:
        return self.can_load or not self._has_val(unit)
