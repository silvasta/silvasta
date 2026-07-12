"""
Decompose Strings with Regex

- Pattern, Names, Matches

"""

from .match import LogPatterns, RegexMatch
from .name import NamePattern
from .parsed_name import ParsedName
from .styled_name import StyledName

__all__: list[str] = [
    "NamePattern",
    "StyledName",
    "ParsedName",
    # match
    "RegexMatch",
    "LogPatterns",
]
