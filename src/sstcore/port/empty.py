"""
Nonething interesting to see here...

- Ghost: type check dummy for temporary abc
- ViewSentinel: enum dispatch dummy for views
- Void: global sentinel created for public use

Sentinel:

Replace None and Any with Type Safe Alternatives
- Avoid Any to erasure the type just for widening the annotation
- Avoid None as unprecise and unpredictable placeholder

Use the VOID Sentinel as Value and as Type!
- number: int | VOID = VOID
- clearly narrows the type afterwards,
  like after isinstance(number,int) == False
  -> number clearly identified as VOID

                              DependencyLevel.sstcore.port.empty[0]
"""

__all__: list[str] = [
    "Ghost",
    "VOID",
    "May",
    "Maybe",
    "MayBe",
    "sentinel",
    "ViewSentinel",
]


import sys
from typing import TYPE_CHECKING as _TYPECHECKING

if sys.version_info >= (3, 15):
    from builtins import sentinel
else:
    from typing_extensions import sentinel


VOID = sentinel("VOID")

type May[Some] = Some | VOID
type MayBe[Some] = Some | VOID
type Maybe[Some] = Some | VOID


class _GhostBaseEradicator:
    """Create class dummy that gets filtered out at composition"""

    def __mro_entries__(self, _bases: tuple) -> tuple:
        """The Trick: Empty tuple in __mro_entries__ eradicates the Ghost"""
        return ()


Ghost = _GhostBaseEradicator()


class ViewSentinel:
    """Imitate ViewMixin to replace None in View selection pipeline"""

    def __cli__(self):
        raise NotImplementedError

    def __log__(self):
        raise NotImplementedError

    def __rich__(self):
        raise NotImplementedError


if __name__ == "__main__" or _TYPECHECKING and VOID:  # ty:ignore

    def _example_pipeline():  # TODO: more beautiful
        """
        Provide Ghost class imitation that disappears for runtime MRO

        The Idea:
        - show the type checker a full class composition
        - instead (hiddenly) replace the class by the Ghost
        -> enjoy full typing with zero runtime effect

        Current Experience:

        It can help quite well, instead of duck typing with protocols or
        annotations it just does everything desired. Still, the issue
        when the type checker gets scared due to a later on composition...

        It is still a Ghost, nice until it starts to do strange things..

        Recommendation, prepare it as toggle (# with comment) and overall,
        it will save time and it is harmless at runtime, but mocking the
        type checker to hard is not recommended.

                                    DependencyLevel.sstcore.brick.none[0]
        """

        # NEXT: apply the idea with type(.,.,.) and alternating: see ParsedName

        class BaseClass:
            def base_method(self) -> None: ...

        class EarlyMixin:
            def early_method(self) -> None: ...

        if _TYPECHECKING:
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

        if _TYPECHECKING:
            # Show the type checker the next step
            class _MediumStateMixin(EarlyMixin, BaseClass): ...
        else:
            _MediumStateMixin = Ghost  # noqa:N806

        class LateMixin(_MediumStateMixin):
            def do_work(self) -> None:
                pass

        class FinalWorker(LateMixin, IntermediateMixin, EarlyMixin, BaseClass):
            pass

    def _impossible_type_mock(*classes: type):  # REMOVE:
        """Dynamic MRO unpacking fails... proves why the static Ghost is needed!"""

        if not _TYPECHECKING:
            return Ghost

        class _TypeCheckerGhost(*classes): ...  # ty:ignore

        return _TypeCheckerGhost

    def _senti_check():
        #
        #  LINE: -- Tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --

        print(f"Sentinel {sys.version_info} prepared: {sentinel}")

        def _narrow_type(path: int | VOID = VOID):
            from typing import reveal_type

            if path is VOID:
                reveal_type(path)
            else:
                reveal_type(path)

        print(VOID)
        print("\n", "repr:")
        print(repr(VOID))
        print("\n", "dir:")
        print(dir(VOID))
