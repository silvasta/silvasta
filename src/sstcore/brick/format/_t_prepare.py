from collections import Counter


class FrequencyGate:
    def __init__(self, inner: ViewFn, noisy_after: int = 3) -> None:
        self.inner = inner
        self.noisy_after = noisy_after
        self.seen: Counter[str] = Counter()

    def __call__(self, value: Any, interp: Interpolation) -> Piece:
        key = f"{type(value).__qualname__}:{interp.expression}"
        self.seen[key] += 1
        if self.seen[key] > self.noisy_after:
            return Text(
                f"{type(value).__name__}·{self.seen[key]}", style="dim"
            )
        return self.inner(value, interp)


def sanitize(template: Template, max_str: int = 120) -> Template:
    def wrap(i: Interpolation) -> Interpolation:
        v = i.value
        if is_sensitive(i.expression):
            v = "***"
        elif isinstance(v, str) and len(v) > max_str:
            v = v[: max_str - 1] + "…"
        return Interpolation(v, i.expression, i.conversion, i.format_spec)

    return map_template(template, wrap)


def render_plain(template: Template) -> str:
    parts: list[str] = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
            continue
        value = apply_conversion(item.value, item.conversion)
        spec = item.format_spec
        try:
            parts.append(
                format(value, spec)
                if spec and looks_like_format_spec(spec)
                else str(value)
            )
        except TypeError, ValueError:
            parts.append(str(value))
    return "".join(parts)
