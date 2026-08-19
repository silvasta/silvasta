"""
Provide Ghost class imitation that disappears for runtime MRO

- Ghost: Empty class with empty MRO entries
- example_pipeline: check how to wire it

The Idea:
  - show the type checker a full class composition
  - instead (hiddenly) replace the class by the Ghost
  -> enjoy full typing with zero runtime effect

"""

__all__: list[str] = [
    "Ghost",
    "example_pipeline",
]

from typing import TYPE_CHECKING


class _GhostBaseEradicator:
    """Create class dummy that gets filtered out at composition"""

    def __mro_entries__(self, _bases: tuple) -> tuple:
        """The Trick: Empty tuple in __mro_entries__ eradicates the Ghost"""
        return ()


Ghost = _GhostBaseEradicator()


def example_pipeline():
    """Show the type check mock workflow"""

    # LATER: inject printer and show colorized MRO tables

    class BaseClass:
        def base_method(self) -> None: ...

    class EarlyMixin:
        def early_method(self) -> None: ...

    if TYPE_CHECKING:
        # Show the type checker the desired class hierarchy
        class _EarlyStateMixin(EarlyMixin, BaseClass): ...
    else:
        # Place instead an MRO-empty ghost object there
        _EarlyStateMixin = _GhostBaseEradicator()  # noqa:N806

    class IntermediateMixin(_EarlyStateMixin):
        def late_method(self) -> None:
            """IDE and type checker still see everything!"""
            self.base_method()
            self.early_method()

    if TYPE_CHECKING:
        # Show the type checker the next step
        class _MediumStateMixin(EarlyMixin, BaseClass): ...
    else:  # Assign it directly! Do not use the `class` keyword.
        _MediumStateMixin = Ghost

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
