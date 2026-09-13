"""
Experiments with python.bisect

Idea: Simple setup that absorbs complexity ready for fast apply
- Maintain sorted list of (threshold, value) pairs
- Use bisect to find the matching bucket in O(log n)
- Control behavior with policies

Bisect semantics:
- Sorted list, ascending! left is low, right is high
- bisect_left: insertion point to the LEFT of equal elements
- bisect_right: insertion point to the RIGHT of equal elements

"""

# IMPORTANT: complete refactor of this, split all to port/brick/maybe util

__all__: list[str] = [
    "BisectData",
    "BisectExecutor",
    "BoundaryPolicy",
    "InsertPolicy",
    "run_example",
]


from bisect import bisect_left, bisect_right, insort_left, insort_right
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps
from typing import Any, Literal, Protocol, Self, overload


# MOVE: port
class BisectNormalizing[TargetT: int | float | BisectHolding](Protocol):
    def __call__(self, target: TargetT, *args, **kwargs): ...


# MOVE: port
class BisectHolding[ThreshT: int | float, DisplayT: Any](Protocol):
    """Define the Shape of the BisectDTOs"""

    @property
    def threshold(self) -> ThreshT:
        """The value for the sorting"""

    @property
    def label(self) -> DisplayT:
        """The value for the return"""

    @staticmethod
    def key(dto: BisectHolding) -> ThreshT:  # INFO: Python 3.14
        """Extract the sorting value from the Self-DTO"""

    @classmethod
    def _normalize(  # MOVE: maybe in base class, not in Protocol
        cls, func: BisectNormalizing[ThreshT | Self]
    ) -> BisectNormalizing[ThreshT | Self]:
        """Extract the value for sorting from the DTO"""


@dataclass
class BisectData:
    # TODO: Parametrize, but what?
    # - threshold: for sure int, most likely float, what else?
    # - label: Any? can be a string but as well some random object,
    #   -> maybe use Stringable, general object with __str__(self)?
    """Store threshold for bisectional comparison and corresponing value"""

    thresh: int  # NEXT: -> threshold
    value: str  # NOTE: maybe value is to easy to misunderstand, -> label?

    def __str__(self) -> str:  # MOVE: to base class
        return f"{self.thresh}: {self.value}"

    def __repr__(self) -> str:  # MOVE: to base class
        return f"{type(self).__name__}({self})"

    @staticmethod
    def key(dto: BisectData) -> int:
        # NEXT: this into general base class?
        # - yes: when is ever something returned here that is not self.threshold?
        # - no: maybe keep it more flexible, delay decision until needed?
        # maybe a DTO will hold another class that provides the threshold,
        # then something like return dto.my_object.important_value is needed?
        """Provide executable that defines the lookup threshold"""
        return dto.thresh

    @staticmethod
    def normalize(func: Callable) -> Callable:  # TODO: parametrize callable
        # NEXT: this into general base class!
        # -> together with subhook like _normalize with NotImplementedError
        # IDEA: this or use ArgCast as decorator, processing the subhook
        """Extract integer threshold from int or BisectData signature"""

        @wraps(func)  # TODO: parametrize wrapper
        def wrapper(self, target: BisectData | int, *args, **kwargs) -> Any:
            # MOVE: the normalizing part to subhook
            thresh: int = (
                target.thresh if isinstance(target, BisectData) else target
            )
            return func(self, thresh, *args, **kwargs)

        return wrapper


class InsertPolicy(Enum):  # MOVE: port
    """
    Dictate behavior for inserting threshold that already exists

    - ALLOW_LEFT: Place new duplicate BEFORE existing ones
    - ALLOW_RIGHT: Place new duplicate AFTER existing ones
    - OVERWRITE: Replace the existing data at the threshold (left)
    - RAISE: Throw ValueError on duplicated insertion
    """

    OVERWRITE = auto()
    ALLOW_LEFT = auto()
    ALLOW_RIGHT = auto()
    RAISE = auto()


class BoundaryPolicy(Enum):  # MOVE: port
    """
    Dictate mathematical boundaries during lookup

    - INCLUSIVE (>=) bisect_right: Evaluate to its own tier for exact match
    - EXCLUSIVE (>) bisect_left: Fall back to the previous tier for exact match
    """

    INCLUSIVE = auto()
    EXCLUSIVE = auto()


class BisectExecutor:
    """
    Manage Bisectional List

    - Get the corresponing value in log(n)
    - The list must always be sorted!
      - (Ascending: lowest first/left to highest/right)
    """

    def __init__(
        self,
        insert_policy: InsertPolicy = InsertPolicy.RAISE,
        boundary_policy: BoundaryPolicy = BoundaryPolicy.INCLUSIVE,
    ):
        self.data: list[BisectData] = []
        self._insert_policy: InsertPolicy = insert_policy
        # LATER: descriptor, but: careful for _insert_policy! especially ALLOW*
        self._boundary_policy: BoundaryPolicy = boundary_policy

    def __str__(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
        data: str = "\n".join(f"({d})" for d in self.data)
        # LATER: format with indent etc.
        return f"{self}[\n{data}\n]" if data else f"{self}[...]"

    @property
    def thresholds(self) -> list[int]:
        """Flatten all thresholds to list"""
        return [item.thresh for item in self.data]

    @property
    def values(self) -> list[str]:
        """Flatten all values to list"""
        return [item.value for item in self.data]

    def attach(self, threshs: list[int], values: list[str]) -> Self:
        # RENAME: attach is covered from DecoratorRegistry!
        # - might be possible to change at both locations
        """Provide Executor with updated internal data"""
        for thresh, value in zip(threshs, values, strict=True):
            self.add(thresh, value)
        return self

    def add(self, thresh: int, value: str) -> Any:
        # RENAME: adapt to others, sequence of items desired
        """Create and insert DTO as new item"""
        data = BisectData(thresh, value)
        self.add_dto(data)

    def add_dto(self, data: BisectData) -> Any:
        """Attach new item, Decide on Tie by interal policy or Raise"""

        match self._insert_policy:
            case InsertPolicy.ALLOW_LEFT:
                self.attach_left(new_data=data)

            case InsertPolicy.ALLOW_RIGHT:
                self.attach_right(new_data=data)

            case InsertPolicy.RAISE:
                if data in self:
                    message = f"Thresh[{data.thresh}] already exists!"
                    self._fail(message, data, self.data, strict=True)
                self.attach_right(new_data=data)

            case InsertPolicy.OVERWRITE:
                if data in self:
                    # NOTE: assuming target is only duplicated once in list
                    # - valid if InsertPolicy was never on ALLOW_* before
                    idx: int = self.target_index(target=data)
                    old_data: BisectData = self.data[idx]
                    print(f"Override: {old_data=} -> new_{data=}")
                    self.data[idx] = data  # LATER: add log here
                else:
                    self.attach_right(new_data=data)

    def attach_left(self, new_data: BisectData):
        """Attach new item on position < existing threshold members"""
        insort_left(self.data, new_data, key=BisectData.key)

    def attach_right(self, new_data: BisectData):
        """Attach new item on position > existing threshold members"""
        insort_right(self.data, new_data, key=BisectData.key)

    @overload
    def target_index(self, target: int) -> int: ...

    @overload
    def target_index(self, target: BisectData) -> int: ...

    @BisectData.normalize
    def target_index(self, thresh: int) -> int:
        """
        Provide index where new DTO with incoming thresh is added

        - Attach from left side for multiple existing DTOs with same tresh
          - (avoid this by consequently using the Policies, no switch!)
        """
        return bisect_left(self.data, thresh, key=BisectData.key)

    @overload
    def __contains__(self, target: int) -> bool: ...

    @overload
    def __contains__(self, target: BisectData) -> bool: ...

    @BisectData.normalize
    def __contains__(self, thresh: int) -> bool:
        """Check if threshold exists in exactly one O(log(N)) pass"""
        idx: int = self.target_index(thresh)
        return idx != len(self.data) and self.data[idx].thresh == thresh

    # LATER: @BisectData.normalize
    def get_index(self, thresh: int) -> int:
        """Match item position depending on internal policy"""

        match self._boundary_policy:
            case BoundaryPolicy.EXCLUSIVE:
                return self.left_index(thresh)

            case BoundaryPolicy.INCLUSIVE:
                return self.right_index(thresh)

    # LATER: @BisectData.normalize
    def left_index(self, thresh: int) -> int:
        """
        Match Exclusive tier boundaries ( > ) for existing data

        - For threshold 10: incoming lookup of 10 evaluates to lower tier
        """
        left: int = bisect_left(self.data, thresh, key=BisectData.key)
        return left - 1

    # LATER: @BisectData.normalize
    def right_index(self, thresh: int) -> int:
        """
        Match Inclusive tier boundaries ( >= ) for existing data

        - For threshold 10: incoming lookup of 10 evaluates exactly to 10
        """
        right: int = bisect_right(self.data, thresh, key=BisectData.key)
        return right - 1

    def _fail(self, message: str, *args, strict: bool) -> None:
        if not strict:  # LATER: log
            print(message, "-> using fallback to None")
        else:
            raise ValueError(message, *args)

    @overload
    def __call__(self, thresh: int, strict: Literal[True] = True) -> str: ...
    @overload
    def __call__(
        self, thresh: int, strict: Literal[False] = False
    ) -> str | None: ...

    # LATER: @BisectData.normalize?
    def __call__(self, thresh: int, strict: bool = True):
        """Provide the value corresponing to the matching threshold"""

        if not self.data:
            message = f"{self} has no member, fill before access!"
            return self._fail(message, strict=strict)

        if (index := self.get_index(thresh)) < 0:
            message = f"Incoming Thresh[{thresh}] below Min[{self.data[0]}]!"
            return self._fail(message, thresh, self.data, strict=strict)

        return self.data[index].value


def run_example(  # MOVE: sstcore/../../examples/show_bisect.py
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
    executor.add_dto(data=BisectData(thresh=100, value="priority_again"))
    print(repr(executor))

    print(f"100 inclusive evaluates to: {executor(100)}")  # priority
    executor._boundary_policy = BoundaryPolicy.EXCLUSIVE
    print(f"100 exclusive evaluates to: {executor(100)}")  # standard

    dto = BisectData(thresh=22, value="hello")
    print(f"{dto=} -> {executor.target_index(dto)=}")
    dto = BisectData(thresh=-5, value="hello")
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
    run_example()
