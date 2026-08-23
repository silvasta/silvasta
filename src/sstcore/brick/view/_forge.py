"""
Define common Views and Defaults

- view: universal tool

"""

# TODO: defaults for regular classes

from typing import TYPE_CHECKING, Any, Self, cast, overload

__all__: list[str] = [
    "view",
]

from ._compose import ViewComposer
from ._raise import ViewError
from ._registry import Cli, Log, Repr, Rich, Str, ViewRegistry

type ViewArg = Cli | Str | Rich | Repr | Log


class ViewInjector(ViewComposer):
    """view Distributor: Inject or Build with Preset Views or Modify"""

    extra_mixins: tuple[type, ...] = ()

    @overload
    def __call__[Target: type](self, cls: Target, /) -> Target: ...

    @overload
    def __call__(self, /) -> type: ...

    @overload
    def __call__(
        self,
        *args: ViewArg,
        **kwargs: ViewArg,  # NEXT: why??
    ) -> Self: ...

    def __call__(
        self,
        *args: ViewArg,  # LATER: allow for mixins not in Enum registries
        cli: Cli = Cli.OFF,
        string: Str = Str.OFF,
        rich: Rich = Rich.OFF,
        repr: Repr = Repr.OFF,
        log: Log = Log.OFF,
    ) -> Self:  # AI: Self???

        selected_views: dict[str, ViewRegistry] = {}

        for arg in args:
            if arg.category in selected_views:
                raise ViewError(arg.fail_info("Duplicated Argument!"))
            selected_views[arg.category] = arg

        # IDEA:  Use ViewBuilder().all_enums()??
        default_views: list[ViewRegistry] = [cli, string, rich, repr, log]

        for default in default_views:
            if default.category not in selected_views:
                selected_views[default.category] = default

        return ViewComposer(**selected_views)  # ty:ignore -- shows arg fail

    def __call__builder(
        self, cls: type | None = None, **mixin_overrides_and_additionals
    ) -> type:
        """Inject composed mixins to decorated target or build class"""
        return self.build() if cls is None else self.inject(cls)

    def __call__g46(
        self, first: Any = None, /, *rest: Any, **kwargs: Any
    ) -> Any:
        if _is_target_class(first):
            if rest or kwargs:
                raise TypeError(
                    "view(cls) injects; configure with view(*ViewArg, **enums) "
                    "or view.plus(*mixins, **enums)"
                )
            return self.inject(first)

        if first is None and not rest and not kwargs:
            return self.build()

        args: tuple[ViewArg, ...]
        if first is None:
            args = ()
        else:
            args = cast(tuple[ViewArg, ...], (first, *rest))
        return self._reconfigure(*args, **kwargs)

    def _reconfigure(self, *args: ViewArg, **kwargs: ViewArg) -> Self:
        changes: dict[str, ViewRegistry] = dict(kwargs)
        seen: set[str] = set()
        for arg in args:
            key = arg.category
            if key in seen:
                raise ViewError(arg.fail_info("Duplicated Argument!"))
            seen.add(key)
            if key in changes and changes[key] is not arg:
                raise ViewError(
                    arg.fail_info("Conflicts with keyword argument!")
                )
            changes[key] = arg
        return self.evolve(**changes)


def _is_target_class(obj: object) -> bool:
    # REMOVE:
    # ViewArg members are Enums, never classes — this split is reliable.
    return isinstance(obj, type) and not isinstance(obj, ViewRegistry)


class ViewPresets:
    pydantic = ViewComposer(
        cli=Cli.TABLE,
        string=Str.NAME,
        rich=Rich.MODULE,
        repr=Repr.OFF,
        log=Log.DATA,
    )

    printer = ViewComposer(
        cli=Cli.HEADER,
        string=Str.MODULE,
        rich=Rich.SHORT,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )

    safe_typer = ViewComposer(
        cli=Cli.PANEL,
        string=Str.SHORT,
        rich=Rich.MODULE,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )
    functor = ViewComposer(
        cli=Cli.PANEL,
        string=Str.NAME,
        rich=Rich.MODULE,
        log=Log.DEBUG,
        repr=Repr.DATA,
    )


class View(ViewComposer, ViewPresets): ...


view = View()

if TYPE_CHECKING:
    _instance_check: Injector = view
    _class_check: type[Injector] = View
