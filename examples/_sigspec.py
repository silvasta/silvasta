from typing import reveal_type

from sstcore.brick.call._signature import SigSpec
from sstcore.brick.field._strategy import MorphingField, StrategyField
from sstcore.port.casting import LspViolation
from sstcore.port.primitives._params import Kwargs

# 1. SigSpec operators
base = SigSpec.detect(lambda a, b, c=1: None)
kw_b = SigSpec.detect(lambda a, *, b: None)

# Intersection & Difference on `both`
common = base & kw_b  # -> (a, *, b)
lost = (
    base - kw_b
)  # -> (b, /, c=1)  -- b lost POS access, c was dropped completely

# Violation extraction via >> and containment via `in` / `>=`
violations = base >> kw_b

# print(f"{violations:nv}")
# print(f"{LspViolation.REDUCED_MAX_POS | LspViolation.LOST_POS_ACCESS:nv}")

print(violations)
print(LspViolation.REDUCED_MAX_POS | LspViolation.LOST_POS_ACCESS)

print(
    violations == (LspViolation.REDUCED_MAX_POS | LspViolation.LOST_POS_ACCESS)
)
print(kw_b not in base)


# 2. StrategyField & MorphingField with tolerance
class Processor:
    @StrategyField
    def compute(self, x: int, y: int = 1) -> int:
        return x + y

    @StrategyField(tolerance=LspViolation.SINK_CALLBACK)
    def on_done(self, status: int, detail: str = "") -> None:
        pass

    @MorphingField
    def transform(self, data: str) -> str:
        return data.strip()


proc = Processor()

print(f"{Kwargs.vars(proc):nv}")


# Valid LSP replacement (contravariant parameter widening int -> int | float, extra optional param)
def fast_compute(x: int | float, y: int = 1, scale: int = 2) -> int:
    return int(x + y) * scale


proc.compute.switch(fast_compute)
print(proc)
print(f"{Kwargs.vars(proc):nv}")
print(proc.compute)
reveal_type(proc.compute)
print(proc.compute.engine)

print(proc.compute(3, 4) == 14)
print(proc.compute.violation == LspViolation.ZERO)


# SINK_CALLBACK tolerance allows dropping optional keyword parameters and changing return type
def minimal_sink(status: int) -> bool:
    return status == 200


proc.on_done = minimal_sink
assert proc.on_done.violation == (
    LspViolation.REDUCED_MAX_POS
    | LspViolation.DROPPED_KW_NAME
    | LspViolation.DISJOINT_RETURN_TYPE
)

# MorphingField tracks violations on arbitrary signature changes
proc.transform.morph(lambda a, b, c: [a, b, c])
assert proc.transform.violation != LspViolation.ZERO
