from importlib.metadata import PackageNotFoundError, version

try:  # show pyproject.toml package name
    __version__: str = version("silvasta")
except PackageNotFoundError:
    __version__ = "unknown"


__all__: list = ["__version__"]
