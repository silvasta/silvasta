"""Temporary store ideas"""

from typing import Any

from rich.control import strip_control_codes

# NEXT: mix with styled_name.StyledName


class StyledName:
    """
    Template that can render both plain and Rich strings.

    Usage:
        template = "{project} v{version} — {status}"
        rich_template = "[bold cyan]{project}[/] v[dim]{version}[/] — [green]{status}[/]"

        sn = StyledName(plain_template=template, rich_template=rich_template, keys=["project","version","status"])

        sn.as_str(project="sstcore", version="1.2.3", status="ready")
        sn.as_rich(project="sstcore", version="1.2.3", status="ready")
    """

    # TASK: compary with old StyledName, select best forward double parser

    __slots__ = ("plain_template", "rich_template", "keys")

    def __init__(
        self, plain_template: str, rich_template: str, keys: list[str]
    ):
        self.plain_template = plain_template
        self.rich_template = rich_template
        self.keys = keys

    @classmethod
    def from_rich_template(
        cls, rich_template: str, keys: list[str]
    ) -> StyledName:
        """
        Автоматически получить plain_template из rich_template, удалив Rich-теги.

        Это как раз твой кейс: один шаблон со стилями → plain и rich.
        """
        # Очень простой strip: убираем [tag] и [/tag], оставляя содержимое
        import re

        plain = re.sub(r"\[[^\]]*\]", "", rich_template)
        return cls(
            plain_template=plain, rich_template=rich_template, keys=keys
        )

    def _check(self, **values: Any) -> None:
        missing = set(self.keys) - set(values.keys())
        if missing:
            raise ValueError(f"Missing values for keys: {missing}")

    def as_str(self, **values: Any) -> str:
        self._check(**values)
        return self.plain_template.format(**values)

    def as_rich(self, **values: Any) -> str:
        self._check(**values)
        return self.rich_template.format(**values)

    def as_clean(self, **values: Any) -> str:
        """Plain text без Rich-тегов — для логов, JSON, конфигов."""
        rich_str = self.as_rich(**values)
        return strip_control_codes(rich_str)


class AlicaDataHandler:
    # Шаблон один раз, в классе или в конфиге
    _NAME_TEMPLATE = StyledName.from_rich_template(
        rich_template="[bold red]{handler}[/] ({green}{tree_dag}[/] and {green}{internal_dag}[/])",
        keys=["handler", "tree_dag", "internal_dag"],
    )

    def __str__(self) -> str:
        return self._NAME_TEMPLATE.as_str(
            handler=type(self).__name__,
            tree_dag=self._tree_dag_name(),
            internal_dag=self._internal_dag_name(),
        )

    def __rich__(self) -> str:
        return self._NAME_TEMPLATE.as_rich(
            handler=type(self).__name__,
            tree_dag=self._tree_dag_name(),
            internal_dag=self._internal_dag_name(),
        )


class GeminiDataHandler:
    _NAME_TEMPLATE = StyledName.from_rich_template(
        rich_template="[bold red]{handler}[/] ({green}{tree_dag}[/] ...)",
        keys=["handler", "tree_dag", "internal_dag"],
    )

    def __str__(self) -> str:
        return self._NAME_TEMPLATE.as_clean(**self._get_template_kwargs())

    def __cli__(self) -> str:
        return self._NAME_TEMPLATE.as_rich(**self._get_template_kwargs())
