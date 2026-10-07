"""
Play around with Format

- brick.format

"""

from sstcore.brick.format.text import case
from sstcore.port.calling import Calling

example_inputs: list[str] = [
    "String to Cases",
    "Hello_ALL",
    "test_case_three",
    "newFunctor",
    "Krr=992NNS",
]


strategies: list[Calling[[str], str]] = [
    # IDEA: iterate over module?
    case.to_snake,
    case.to_camel,
    case.to_pascal,
    case.to_kebab,
]

for strategy in strategies:
    print("--- " * 5)
    print(f"Start of: {strategy.__name__}")
    print()
    for string in example_inputs:
        print(f"{string}\n{strategy(string)}\n")
