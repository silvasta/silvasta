"""
Support Composer and others with class assemble tools

- IDEA: use .registry for advanced setup

"""

__all__: list[str] = [
    "combine_mixins",
]


def combine_mixins(  # LATER: this but with like a mix plan
    registered: tuple[type, ...],
    extra: tuple[type, ...],
    *,
    prepend: bool = True,
) -> tuple[type, ...]:
    """Place ephemeral mixins before (override) or after (fallback) the recipe"""
    if not extra:
        return registered
    return extra + registered if prepend else registered + extra


# NEXT: Tuple Registry
# - add = rebuild or error if locked
# - encode rules, similar like above
# - visualize with index
# - sort! rebuild and apply new sorting
# - no mixing here!
# -> only gatekeeper for new mixins and order
