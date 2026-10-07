"""
Show the Wiring of the nonesense Pipeline

-
"""

__all__: list[str] = [
    "example_pipeline",
]

from typing import TYPE_CHECKING

from ._ghost import Ghost


def example_pipeline():
    """Show the type check mock workflow"""

    # NEXT: apply the idea with type(.,.,.) and alternating: see ParsedName

    class BaseClass:
        def base_method(self) -> None: ...

    class EarlyMixin:
        def early_method(self) -> None: ...

    if TYPE_CHECKING:
        # Show the type checker the desired class hierarchy
        class _EarlyStateMixin(EarlyMixin, BaseClass): ...
    else:
        # Place instead an MRO-empty ghost object there
        _EarlyStateMixin = Ghost  # noqa:N806

    class IntermediateMixin(_EarlyStateMixin):
        def late_method(self) -> None:
            """IDE and type checker still see everything!"""
            self.base_method()
            self.early_method()

    if TYPE_CHECKING:
        # Show the type checker the next step
        class _MediumStateMixin(EarlyMixin, BaseClass): ...
    else:  # Assign it directly! Do not use the `class` keyword.
        _MediumStateMixin = Ghost  # noqa:N806

    class LateMixin(_MediumStateMixin):
        def do_work(self) -> None:
            pass

    class FinalWorker(LateMixin, IntermediateMixin, EarlyMixin, BaseClass):
        pass


def _impossible_type_mock(*classes: type):
    """Dynamic MRO unpacking fails... proves why the static Ghost is needed!"""

    if not TYPE_CHECKING:
        return Ghost

    class _TypeCheckerGhost(*classes): ...

    return _TypeCheckerGhost
