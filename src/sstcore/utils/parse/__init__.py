"""
Decompose Strings with Regex

- Pattern, Names, Matches

"""

from ._match import LogMatcher, MatchRule, RegexMatch, RegexMatchBox

__all__: list[str] = [
    "RegexMatch",
    "MatchRule",
    "RuleHandler",
    "RegexMatchBox",
    "LogMatcher",
]
