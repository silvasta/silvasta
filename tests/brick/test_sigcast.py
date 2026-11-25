import pytest

from sstcore.brick.call._signature import SigSpec
from sstcore.brick.field._strategy import (
    BoundStrategy,
    MorphingField,
    StrategyField,
)
from sstcore.port.casting import LspViolation


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


def test_sigspec_operators_and_combined_explain() -> None:
    base = SigSpec.detect(lambda a, b, c=1: None)
    kw_b = SigSpec.detect(lambda a, *, b: None)

    violations = base >> kw_b
    expected = (
        LspViolation.REDUCED_MAX_POS
        | LspViolation.LOST_POS_ACCESS
        | LspViolation.DROPPED_KW_NAME
    )
    assert violations == expected
    assert kw_b not in base

    # Composite IntFlag explanation synthesis via ExplainedTuple.combine fallback
    explained = violations.explain
    assert explained.origin == violations
    assert f"{violations:nv}"


def test_strategy_field_switch_and_sync() -> None:
    proc = Processor()
    bound = proc.compute
    assert isinstance(bound, BoundStrategy)
    assert not bound.is_overridden
    assert bound(3, 4) == 7

    def fast_compute(x: int | float, y: int = 1, scale: int = 2) -> int:
        return int(x + y) * scale

    proc.compute.switch(fast_compute)

    # Previously acquired BoundStrategy reference stays synchronized
    assert bound.is_overridden
    assert bound.func is fast_compute
    assert bound.bind is False
    assert bound(3, 4) == 14
    assert bound.violation == LspViolation.ZERO

    # Reset restores baseline method
    bound.reset()
    assert not bound.is_overridden
    assert bound.bind is True
    assert bound(3, 4) == 7


def test_strategy_field_rejects_lsp_violation_and_morph() -> None:
    proc = Processor()

    def incompatible(x: str) -> str:
        return x

    with pytest.raises(TypeError):
        proc.compute.switch(incompatible)

    with pytest.raises(TypeError):
        proc.compute = incompatible

    with pytest.raises(TypeError):
        proc.compute.morph(incompatible)


def test_strategy_field_sink_callback_tolerance() -> None:
    proc = Processor()

    def minimal_sink(status: int) -> bool:
        return status == 200

    proc.on_done = minimal_sink
    assert proc.on_done(200) is True
    assert proc.on_done.violation == (
        LspViolation.REDUCED_MAX_POS
        | LspViolation.DROPPED_KW_NAME
        | LspViolation.DISJOINT_RETURN_TYPE
    )


def test_morphing_field_tracks_violations() -> None:
    proc = Processor()
    assert proc.transform("  hello ") == "hello"
    assert proc.transform.violation == LspViolation.ZERO

    proc.transform.morph(lambda a, b, c: [a, b, c])
    assert proc.transform(1, 2, 3) == [1, 2, 3]
    assert proc.transform.violation != LspViolation.ZERO

    del proc.transform
    assert proc.transform("  world ") == "world"
    assert proc.transform.violation == LspViolation.ZERO
