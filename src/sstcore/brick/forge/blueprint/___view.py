"""
Idea: Replace View Mixin Injection

- use a direct meta approach instead of mixing everything

Next: Evaluate pro/con of both approaches

"""

from typing import TYPE_CHECKING


class ViewMeta(type):
    def __new__(mcs, name, bases, namespace):
        # 1. Look for your fluent configuration, or provide a default
        view_config = namespace.get("__views__", None)

        if view_config:
            # 2. Resolve your enums and .plus() mixins into actual functions
            cli_func = view_config.resolve_cli()
            log_func = view_config.resolve_log()

            # 3. Inject them directly as dunders
            namespace["__cli__"] = cli_func
            namespace["__log__"] = log_func

            # If you want them as classmethods (like your PathGuard setup):
            # namespace['__cli__'] = classmethod(cli_func)

        return super().__new__(mcs, name, bases, namespace)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Usage
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

if TYPE_CHECKING:
    from sstcore.brick.view import Cli, Str, view


class CustomFormatting: ...


class SystemNode(metaclass=ViewMeta):
    __views__ = view(Cli.PANEL, Str.NAME).plus(CustomFormatting)

    def __init__(self, val):
        self.val = val
