from collections import Counter
from string.templatelib import Interpolation
from typing import Any

from rich.text import Text


class FrequencyGate:
    def __init__(self, inner: ViewFn, noisy_after: int = 3) -> None:
        self.inner = inner
        self.noisy_after = noisy_after
        self.seen: Counter[str] = Counter()

    def __call__(self, value: Any, interp: Interpolation) -> Piece:
        key = f"{type(value).__qualname__}:{interp.expression}"
        self.seen[key] += 1
        if self.seen[key] > self.noisy_after:
            return Text(
                f"{type(value).__name__}·{self.seen[key]}", style="dim"
            )
        return self.inner(value, interp)
