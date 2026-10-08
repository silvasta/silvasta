"""
Provide Test Data for Stacking Experiments and Examples

-
"""

__all__: list[str] = [
    # string
    "NORMALIZERS",
    "SANITIZERS",
    "FORMATTERS",
    # color
    "ANSI_COLORS",
    "ANSI_MODIFIERS",
    "ANSI_RESET",
    # random
    "ATTR1",
    "ATTR2",
    "ATTR3",
]


import re
import unicodedata
from collections.abc import Callable

from ...port.stacking import LayerData, Map

#  LINE: -- String Pipeline-- -- - -- -- - -- -- - -- -- - -- -- - -- --


NORMALIZERS: LayerData[str] = {
    "nfc": lambda s: unicodedata.normalize("NFC", s),
    "lower": str.lower,
    "upper": str.upper,
    "casefold": str.casefold,
}
SANITIZERS: LayerData[str] = {
    "strip": str.strip,
    "collapse": lambda s: re.sub(r"\s+", " ", s),
    "alnum": lambda s: re.sub(r"[^0-9A-Za-z ]+", "", s),
}
FORMATTERS: LayerData[str] = {
    "title": str.title,
    "repr": repr,
}


#  LINE: -- ANSI Color Pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --


ANSI_COLORS: Map[str] = {
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
}
ANSI_MODIFIERS: Map[str] = {
    "bold": "\033[1m",
    "underline": "\033[4m",
}
ANSI_RESET: str = "\033[0m"


#  LINE: -- Random Tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --


ATTR1: Map[int] = {
    "key11": 2,
    "key12": 3,
    "key13": 5,
}

ATTR2: Map[str] = {
    "key21": "hello",
    "key22": "bye",
}

ATTR3: Map[Callable[[str], str]] = {  # TODO: CallingType
    "key31": str.lower,
    "key32": str.capitalize,
    "key33": str.upper,
}
