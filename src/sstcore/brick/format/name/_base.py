"""
Provide view and basic functionalities for Names

                                                      DependencyLevel[0]
"""
# RENAME: _base -> ...
# - not _view! or similar, too much library intern collisions!
# - not _meta! already reserved by MetaClass constructors
# - _zero? maybe even as a general pattern troughout the library?
# - _helper, _util, _...
# - reference to origin:
#   - _baby maybe to controverse
#   - _egg? similar approach as baby but less human centric
#   - _source? maybe too much possibilites for wrong interpretation
#   - _root sounds too valuable for just a few helper and views
# IDEA: completely resolve the module
# - not into the pipeline!
# - when moving the package from brick->forge:
#   - access to functor: resolves naming
#   - access to brick.views.Catalog: below __views__ still to specific...
# - Issue! intended as supplier for view: maybe not brick.viewsforge.view?
#

__all__: list[str] = [
    "BaseName",
]


class BaseName:
    """Hold Meta and Views"""

    pattern: str
    keys: tuple[str, ...]

    @property
    def _name(self):
        return type(self).__name__

    @property
    def _color(self):
        return "cyan"

    def __str__(self):
        return f"{self._name}[:{len(self.keys)}]"

    def __repr__(self):
        return f"{self._name}[{self.keys}'{self.pattern}']"

    def __rich__(self):
        return f"[{self._color}]{self._name}[/][{self.keys}'{self.pattern}']"
