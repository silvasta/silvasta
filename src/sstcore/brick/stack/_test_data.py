"""
Provide Test Stacking Data

- Temporary until implementation is done

"""

import re
import string
import unicodedata
from collections.abc import Callable

from . import _define as port

#  LINE: -- Random Tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --

ATTR1: port.Map[int] = {
    "key11": 2,
    "key12": 3,
    "key13": 5,
}

ATTR2: port.Map[str] = {
    "key21": "hello",
    "key22": "bye",
}

ATTR3: port.Map[Callable[[str], str]] = {  # TODO: CallingType
    "key31": str.lower,
    "key32": str.capitalize,
    "key33": str.upper,
}


#  LINE: -- ANSI -- -- - -- -- - -- -- - -- -- - -- -- - -- --

ANSI_COLORS: port.Map[str] = {
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
}
ANSI_MODIFIERS: port.Map[str] = {
    "bold": "\033[1m",
    "underline": "\033[4m",
}
ANSI_RESET: str = "\033[0m"


#  LINE: -- String -- -- - -- -- - -- -- - -- -- - -- -- - -- --


STRING_NORMALIZERS: port.LayerData[str] = {
    "lower": str.lower,
    "upper": str.upper,
}
STRING_SANITIZERS: port.LayerData[str] = {
    "strip_punct": lambda s: s.translate(
        str.maketrans("", "", string.punctuation)
    ),
    "trim": str.strip,
}

# AI: they below are good examples for T|Callable[T]

NORMALIZERS: port.LayerData[str] = {
    "nfc": lambda s: unicodedata.normalize("NFC", s),
    "lower": str.lower,
    "upper": str.upper,
    "casefold": str.casefold,
}
SANITIZERS: port.LayerData[str] = {
    "strip": str.strip,
    "collapse": lambda s: re.sub(r"\s+", " ", s),
    "alnum": lambda s: re.sub(r"[^0-9A-Za-z ]+", "", s),
}
FORMATTERS: port.LayerData[str] = {
    "title": str.title,
    "repr": repr,
}
