"""
Normalize Inputs for safe handling afterwards

                                                           ModuleLevel[0]
"""

__all__: list[str] = [
    "dict_to_str",
    "dict_to_list",
    "list_to_str",
    "impossible_brackets",
    "format_kv",
]


from typing import Any

# AI_QUESTION: this was the only module from format where I wasn't sure,
# it a transfer from format into this module is absolutely justified...


def dict_to_list(data: dict[str, Any], sep="=") -> list[str]:
    """Format each dict entry to string with separator"""
    return [
        f"{key}{sep}{value}"  #
        for key, value in data.items()
    ]


def list_to_str(strings: list[str], sep=", ") -> str:
    """Concat list of string with separator"""
    return f"{sep}".join(strings)


def dict_to_str(data: dict[str, Any], inner="=", outer=", ") -> str:
    """Concat all formatted entries of dict to single string"""
    strings: list[str] = dict_to_list(data, sep=inner)
    return list_to_str(strings, sep=outer)


def impossible_brackets(key: str) -> str:  # INFO: don't loose this
    """Needed for proper {key}"""
    return f"{{{key}}}"


# AI: this is already named format
def format_kv(
    mapping: dict[str, Any],
    sep: str = "=",
    pair_sep: str = " ",
    quote_strings: bool = False,
) -> str:
    """Format dictionary into key=value pairs for clean str/repr outputs."""
    # IDEA: parametrized and with heavy defaults into Functor-
    pairs = []
    for k, v in mapping.items():
        # AI: here this part looks clearly like reflect/inspect
        val_str = f"'{v}'" if quote_strings and isinstance(v, str) else str(v)
        pairs.append(f"{k}{sep}{val_str}")
    # AI: overall it is a combination of both
    return pair_sep.join(pairs)
