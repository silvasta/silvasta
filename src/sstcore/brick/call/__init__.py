"""
brick.call

- Callable Fragments
- Func input ensured
                                                        reflect(+1)
                              DependencyLevel.sstcore.brick.call[1]
"""

__all__: list[str] = [
    "just_return",
    "validate_signature",
    #
    "ArgCast",
    "ArgCasting",
    "castarg",
]

from ._argcast import ArgCast, ArgCasting, castarg
from ._inspect import validate_signature
from ._some import just_return


# TASK: Components
# - CastInput: TypedDict kwargs
# - CastSpec: holds validation and confirmed data of 1 interception
#   data-structure ideas:
#     - (auto-)dataclass with normalize/validate(/sanitize)
#     - registry with flags: each flag corresponds to 1 casting rule
# - ArgCaster: the loop function:
#   - executes (spec-)validation or regular function, mapped in ArgCast
#   - maybe some caching, preparing new values from ArgCast for CastSpec

# TASK: Main
# - ArgCast: orchestrate plan generation, global registry and decorator

# TASK: Registry
# - no import of sstcore.brick.vault.* as core of registry here!
# - assemble in sstcore.forge.func, maybe with additional later on registration
# - registry:
#   - ensures or warns for (not) loaded entries
#   - shows explanation short and clear or detailed on request
# - overall ensure that nothing is casted that is not wanted,
#   and as many options are easily selectable as possible
# - maybe CasterRegistry containing FlagRuleRegistries per topic
# - use BisectRegistry for different changeable levels of casting?

# IDEA: make each item a Rule:
# - each Rule has a name, a field in Spec and Input and a resolver
# - maybe even as some IntFlag that can be switched fast
