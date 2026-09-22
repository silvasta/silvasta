"""
Provide Test Stacking Data

- Temporary until implementation is done

"""

import string
from collections.abc import Callable

from . import ___define as port

#  LINE: -- Random Tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --

ATTR1: port.AttrType[int] = {
    "key11": 2,
    "key12": 3,
    "key13": 5,
}

ATTR2: port.AttrType[str] = {
    "key21": "hello",
    "key22": "bye",
}

ATTR3: port.AttrType[Callable[[str], str]] = {  # TODO: CallingType
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


#  LINE: -- String -- -- - -- -- - -- -- - -- -- - -- -- - -- --


STRING_NORMALIZERS = {
    "lower": str.lower,
    "upper": str.upper,
}
STRING_SANITIZERS = {
    "strip_punct": lambda s: s.translate(
        str.maketrans("", "", string.punctuation)
    ),
    "trim": str.strip,
}
