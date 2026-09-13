from bisect import bisect_left, bisect_right, insort_left, insort_right
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Literal, Protocol, Self, overload


def main(  # MOVE: sstcore/../../examples/show_bisect.py
    FAIL_ON_EMPTY=False,
    FAIL_ON_MINIMUM=False,
):
    THRESHOLDS: list[int] = [0, 100, 500, 1_000]
    LEVELS: list[str] = ["standard", "priority", "premium", "enterprise"]

    executor: BisectExecutor = BisectExecutor(
        insert_policy=InsertPolicy.OVERWRITE,
        boundary_policy=BoundaryPolicy.INCLUSIVE,
    ).attach(threshs=THRESHOLDS, values=LEVELS)
    print(repr(executor))

    executor.add(thresh=600, value="special")
    executor.add_dto(data=BisectDTO(thresh=100, value="priority_again"))
    print(repr(executor))

    print(f"100 inclusive evaluates to: {executor(100)}")  # priority
    executor._boundary_policy = BoundaryPolicy.EXCLUSIVE
    print(f"100 exclusive evaluates to: {executor(100)}")  # standard

    dto = BisectDTO(thresh=22, value="hello")
    print(f"{dto=} -> {executor.target_index(dto)=}")
    dto = BisectDTO(thresh=-5, value="hello")
    print(f"{dto=} -> {executor.target_index(dto)=}")

    # NOTE: IDE shows: str
    strict_return = executor(10, strict=True)
    # NOTE: IDE shows: str | None
    not_strict_return = executor(10, strict=False)
    print("avoiding unused warning...", strict_return, not_strict_return)

    if FAIL_ON_MINIMUM:
        executor(-5, strict=False)

    if FAIL_ON_EMPTY:
        BisectExecutor()(thresh=1)


if __name__ == "__main__":
    main()
