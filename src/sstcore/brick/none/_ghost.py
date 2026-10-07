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

"""

__all__: list[str] = [
    "Ghost",
]


class _GhostBaseEradicator:
    """Create class dummy that gets filtered out at composition"""

    def __mro_entries__(self, _bases: tuple) -> tuple:
        """The Trick: Empty tuple in __mro_entries__ eradicates the Ghost"""
        return ()


Ghost = _GhostBaseEradicator()
