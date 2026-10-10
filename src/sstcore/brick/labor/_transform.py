"""
Normalize Inputs for safe handling afterwards

                                                           ModuleLevel[0]
"""

__all__: list[str] = [
    "dict_to_str",
    "dict_to_list",
    "list_to_str",
    "stringdict",
    "impossible_brackets",
    "format_kv",
]


from typing import Any


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


def stringdict(self, inner=":=", outer="-|-"):
    """Smash all 3 above into a condensed 1liner"""
    return f"{outer}".join(f"{k}{inner}{v}" for k, v in vars(self).items())


# TODO: combine above/below


def _vars(target, /, sep="\n", map=":="):
    return f"{sep}".join(f" - {k}{map}{v}" for k, v in vars(target).items())


def impossible_brackets(key: str) -> str:  # INFO: don't loose this
    """Needed for proper {key}"""
    return f"{{{key}}}"


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
        val_str = f"'{v}'" if quote_strings and isinstance(v, str) else str(v)
        pairs.append(f"{k}{sep}{val_str}")
    return pair_sep.join(pairs)
