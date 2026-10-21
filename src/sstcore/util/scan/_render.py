from ...port.tree import ApiStyle, AstKind
from ..tree._ast import AstOptions, AstTreeNode, AstTreeNodeG45


def render_ast_tree(  # NOTE: G420
    node: AstTreeNode, style: str = "compact", indent: str = "  "
) -> str:
    """Render tree in different styles. Extend as needed."""
    lines: list[str] = []

    def _recurse(n: AstTreeNode, depth: int = 0) -> None:
        prefix = indent * depth
        lines.append(f"{prefix}{n.display_label}")
        if n.docstring and style != "signatures_only":
            doc_prefix = prefix + indent
            lines.append(f'{doc_prefix}"""{n.docstring}"""')
        for child in n.branches:
            if isinstance(child, AstTreeNode):
                _recurse(child, depth + 1)

    _recurse(node)
    return "\n".join(lines)


# NOTE: G3
def render_api_compact(node: AstTreeNode, indent: int = 0) -> str:
    """Renders the AST Tree into a compact text format."""
    lines = []
    spacer = "    " * indent

    if node.kind == "module":
        if node.docstring:
            lines.append(f'"""{node.docstring}"""\n')
    else:
        prefix = (
            "class "
            if node.kind == "class"
            else ("async def " if "async" in node.kind else "def ")
        )
        lines.append(f"{spacer}{prefix}{node.name}{node.signature}:")
        if node.docstring:
            lines.append(f'{spacer}    """{node.docstring}"""')

        # If it has no branches (e.g., empty class or function), add ellipsis
        if not node.branches and node.kind != "module":
            lines.append(f"{spacer}    ...")

    for branch in node.branches:
        lines.append(
            render_api_compact(
                branch, indent + (1 if node.kind != "module" else 0)
            )
        )

    return "\n".join(lines)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### G45
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def format_api(
    root: AstTreeNodeG45,
    style: ApiStyle = ApiStyle.COMPACT,
    options: AstOptions | None = None,
) -> str:
    options = options or AstOptions()
    match style:
        case ApiStyle.COMPACT:
            return "\n".join(_format_compact(root, options))
        case ApiStyle.STUB:
            return "\n".join(_format_stub(root, options))


def _format_compact(
    node: AstTreeNodeG45, opt: AstOptions, indent: int = 0
) -> list[str]:
    sp = "    " * indent
    lines: list[str] = []

    if node.kind is AstKind.MODULE:
        if opt.include_module_docstring and node.docstring:
            lines.append(f'"""{node.docstring}"""')
            lines.append("")
        for child in node.branches:
            lines.extend(_format_compact(child, opt, indent=0))
            lines.append("")
        return lines

    if node.kind is AstKind.CLASS:
        lines.append(f"{sp}class {node.signature}:")
    elif node.kind is AstKind.ASYNC_DEF:
        ret = f" -> {node.returns}" if node.returns else ""
        lines.append(f"{sp}async def {node.signature}{ret}:")
    elif node.kind is AstKind.DEF:
        ret = f" -> {node.returns}" if node.returns else ""
        lines.append(f"{sp}def {node.signature}{ret}:")
    elif node.kind is AstKind.ASSIGN:
        lines.append(f"{sp}{node.signature}")
        return lines

    if opt.include_docstrings and node.docstring:
        # single-line prefer; multi-line keep simple
        doc = node.docstring.replace("\n", f"\n{sp}    ")
        lines.append(f'{sp}    """{doc}"""')

    if node.branches:
        for child in node.branches:
            lines.extend(_format_compact(child, opt, indent=indent + 1))
    else:
        lines.append(f"{sp}    ...")

    return lines


def _format_stub(
    node: AstTreeNodeG45, opt: AstOptions, indent: int = 0
) -> list[str]:
    # same structure; ellipsis bodies, no nested implementation detail
    # can share helpers with compact later
    raise NotImplementedError
