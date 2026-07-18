"""
Decompose Strings with Regex

- Pattern, Names, Matches

"""  # TODO:

from .match import LogMatcher, MatchRule, RegexMatch, RegexMatchBox
from .name import ColoredName, NameParser, ParsedName, SchemaName

__all__: list[str] = [
    # name
    "NameParser",
    "ParsedName",
    "ColoredName",
    "SchemaName",
    # match
    "RegexMatch",
    "MatchRule",
    "RuleHandler",
    "RegexMatchBox",
    "LogMatcher",
]
