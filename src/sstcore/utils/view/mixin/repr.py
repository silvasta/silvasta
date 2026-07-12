"""
Compose ReprMixins

- Atomize: 1 class with 1 method __repr__
"""


class DataMixin:
    def __repr__(self) -> str:
        attrs = ", ".join(  # COLLECT:
            f"{k}={v!r}"
            for k, v in vars(self).items()
            if not k.startswith("_")
        )
        return f"{type(self).__name__}({attrs})"


class FullReprMixin:
    def __repr__(self) -> str:
        # COLLECT: there is some pattern for repr,log,even cli
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({attrs})"
