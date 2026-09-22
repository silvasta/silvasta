"""
Provide Test Stacking Data

- Temporary until implementation is done

"""

from collections.abc import Callable

type AttrType[Value] = dict[str, Value]


#  LINE: -- Random Tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --

ATTR1: AttrType[int] = {
    "key11": 2,
    "key12": 3,
    "key13": 5,
}

ATTR2: AttrType[str] = {
    "key21": "hello",
    "key22": "bye",
}

ATTR3: AttrType[Callable[[str], str]] = {  # TODO: CallingType
    "key31": str.lower,
    "key32": str.capitalize,
    "key33": str.upper,
}


#  LINE: -- ANSI -- -- - -- -- - -- -- - -- -- - -- -- - -- --

ANSI_COLORS: dict[str, str] = {  # TODO: MappingType
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
}
ANSI_MODIFIERS: dict[str, str] = {  # TODO: MappingType
    "bold": "\033[1m",
    "underline": "\033[4m",
}
ANSI_RESET: str = "\033[0m"
