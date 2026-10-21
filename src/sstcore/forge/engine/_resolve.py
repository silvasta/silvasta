"""
First sketch of a meta resolver

-
"""

__all__: list[str] = [
    "combine_metas",
]


_meta_cache: dict[tuple[type, ...], type] = {}


def combine_metas(*bases):
    """
    Merge metaclass and prevent multiple inheritance conflicts

    Usage: class MyClass(Base1, Base2, metaclass=combine_metas(Base1, Base2)):
    """

    incoming_metas: set[type] = set(type(b) for b in bases)

    if type in incoming_metas and len(incoming_metas) > 1:
        incoming_metas.remove(type)

    filtered_metas: list[type] = [
        candidate
        for candidate in incoming_metas
        if not any(
            issubclass(peer, candidate)
            for peer in incoming_metas
            if peer is not candidate
        )
    ]
    leaf_metas: tuple[type, ...] = tuple(
        sorted(filtered_metas, key=lambda m: m.__name__)
    )

    if len(leaf_metas) == 1:
        return leaf_metas[0]

    if leaf_metas in _meta_cache:
        return _meta_cache[leaf_metas]

    meta_name: str = "DynamicMeta_" + "_".join(m.__name__ for m in leaf_metas)

    combined_meta = type(meta_name, leaf_metas, {})
    _meta_cache[leaf_metas] = combined_meta

    return combined_meta


#  LINE: -- Tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --
if __name__ == "__main__":

    class MetaX(type):
        def __new__(mcs, name, bases, ns):
            ns["x_tagged"] = True
            return super().__new__(mcs, name, bases, ns)

    class MetaY(type):
        def __new__(mcs, name, bases, ns):
            ns["y_tagged"] = True
            return super().__new__(mcs, name, bases, ns)

    class BaseX(metaclass=MetaX):
        """Independent Base Class 1"""

    class BaseY(metaclass=MetaY):
        """Independent Base Class 2"""

    # INFO: test the type checker here:
    # class ConflictingChild(BaseX, BaseY):
    #     """ Uncomment to Show Conflict!
    #     # ^^^ This raises TypeError: metaclass conflict """

    class Child(BaseX, BaseY, metaclass=combine_metas(BaseX, BaseY)):
        """Resolve the MetaConflicts"""

    print(type(Child).__name__)  # Output: DynamicMeta_MetaX_MetaY
    print(Child.x_tagged)  # Output: True
    print(Child.y_tagged)  # Output: True
