# Base of all Projects - `sstcore`

<!-- LATER: as soon as online  -->
<!-- [![PyPI version](https://img.shields.io/pypi/v/sstcore.svg)](https://pypi.org/project/sstcore/) -->
<!-- [![Python versions](https://img.shields.io/pypi/pyversions/sstcore.svg)](https://pypi.org/project/sstcore/) -->

**Collection of frequently used generalized Utils, Functions and Tools.**

`sstcore` serves as the foundation for several of my projects. It provides battle-tested solutions for:

<!-- TODO: -->
<!-- - SafeTyper -->
<!-- - Config with entire Family and Bootstrap  -->
<!-- - Paint -> Printer -> Canvas -> CLI -->
<!-- - like any folder somewhere (maybe group filter/parse) -->

- Filesystem safety and path management (`PathGuard`)
- Opinionated but flexible configuration management (`ConfigManager`)
- Rich logging, printing, and Typer CLI integration

## Features

- **`PathGuard`**: Hybrid decorator + function API for safe path handling, automatic directory creation, unique filenames, rotation, pruning, and relative path helpers.
- **Configuration System**: Pydantic-based settings with `ConfigManager`, `SstSettings`, `SstPaths`, home directory setup, and `.env` support.
- **CLI Helpers**: Seamless integration with Typer (`attach_callback`, `logger_catch`).
- **Utilities**: `Printer`, structured logging setup, time helpers, and more.

## Installation

```bash
# Basic
pip install sstcore

# Recommended
uv add "sstcore[cli]"
# TODO: sync with toml
# With all extras
uv add "sstcore[all]"
```

**Test version:**

```bash
uv add  ...
```

## Quickstart

### PathGuard

```python
from pathlib import Path
from sstcore import PathGuard

# As regular function
log_dir = PathGuard.dir("~/logs/myapp")
config_file = PathGuard.file("config.json", default_content='{"debug": true}')

# As decorator
@PathGuard.dir
def get_output_dir() -> Path:
    return Path("output") / "results"

@PathGuard.unique(ensure_parent=True)
def get_unique_log() -> Path:
    return Path("logs") / "experiment.log"

# Advanced usage
PathGuard.rotate("old_data", "archive/data_v1")
PathGuard.prune("backups/model_", remaining=5)  # keep only 5 newest
```

See `PathGuard.file()`, `.dir()`, `.unique()`, `.rotate()`, `.prune()`, `.find_sequence()`, and the relative path methods (`get_relative_or_name`, `compute_relative`, etc.).

### Configuration System

```python
from sstcore.config import ConfigManager, SstSettings, SstPaths

config = ConfigManager.default_setup()
print(config.project_name)
print(config.settings)
print(config.paths.local_home_dir)

# Access typed components
print(config.defaults.log.level)
```

The system supports master settings files, environment variable loading, and easy subclassing for other projects.

### CLI Integration (with Typer)

```python
import typer
from sstcore.cli import attach_callback, logger_catch

app = typer.Typer()

@logger_catch
@app.command()
def run():
    ...

attach_callback(app)  # attaches logging, config, printer, verbose/quiet flags
```

## Module Overview

- **`sstcore.utils`** — `PathGuard`, `Printer`, `setup_logging`, `day_count`, ...
- **`sstcore.config`** — `ConfigManager`, `SstSettings`, `SstPaths`, `SstDefaults`, ...
- **`sstcore.cli`** — `attach_callback`, `logger_catch`, `monitor`
- **`sstcore.data`** — File helpers

Full API documentation is available in the docstrings and on GitHub.

## License

Apache License 2.0. See [LICENSE](LICENSE) file.
