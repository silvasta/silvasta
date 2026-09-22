"""
Stack the output as input of the next Stack

                                  DependencyLevel.sstcore.brick[0]
"""

from collections.abc import Callable
from typing import Any

from ...port.calling import Calling

_test: Callable = Calling

type StackOr[T] = T | Callable[[T, Any], T]

# IDEA: forward some dto that gets updatede?


def test[T](arg: T) -> StackOr[T]:
    def _logic(arg: T) -> T:
        print("_logic", "test")
        return arg

    called: T = _logic(arg)

    # AI_QUESTION: how to ever dispatch this?
    # return called when next stack not added
    # sounds somhow impossible...

    return test1(called)


def test0[T](arg: T) -> T | Callable[[T, Any], T]:
    def _logic(arg: T) -> T:
        print("_logic", "test0")
        return arg

    called: T = _logic(arg)

    return test1(called)


def test1[T](arg: T) -> T | Callable[[T, Any], T]:
    def _logic(arg: T) -> T:
        print("_logic", "test1")
        return arg

    called: T = _logic(arg)

    return test2(called)


def test2[T](arg: T) -> T | Callable[[T, Any], T]:
    def _logic(arg: T) -> T:
        print("_logic", "test2")
        return arg

    called: T = _logic(arg)

    return called


run1 = test(5)
