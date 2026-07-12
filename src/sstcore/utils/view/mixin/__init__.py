"""
Provide Base Components to create Views

- cli    __cli__
- string __str__
- rich   __rich__
- repr   __repr__
- log    __log__

Exploit shared patterns through common fundamentals:
- Treat str and rich as name where 1 is colorful
- Treat repr and log structured but 1 is flat

Work out individual ideas while building toward a common brand.

"""

__all__: list[str] = [
    "cli",
    "string",
    "rich",
    "repr",
    "log",
]

from . import cli, log, repr, rich, string

# STRATEGY: further developement
# - Iteration 1 completed, each category has sufficient Mixins for first runs
# - Discovered patterns for collecting Data and Names form classes
#   - structure them and apply over all mixins, use .base if needed
#   - create decoupled setup while using similarity for efficience
# - Think about:
#   - additional Parameter in ViewSpec instead of increasing Mixins
#   - additional Support Mixins (to avoid duplicated attach) for:
#     - _func_with_default(self): classes can override or ignore
#     - _special_param: classes can control their color, text, whatever
# Important: iterate over projects to get ideas and figure out needs!
