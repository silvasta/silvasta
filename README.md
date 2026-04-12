# Utils Collection

[![PyPI version](https://img.shields.io/pypi/v/silvasta.svg)](https://pypi.org/project/silvasta/)
[![Python versions](https://img.shields.io/pypi/pyversions/silvasta.svg)](https://pypi.org/project/silvasta/)

**Collection of frequently used generalized Utils, Functions and Tools.**

`silvasta` serves as the foundation for several of my projects. It provides battle-tested solutions for:

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
pip install silvasta

# Recommended
pip install "silvasta[cli]"

# With all extras
pip install "silvasta[all]"
```

**Test version:**

```bash
pip install -i https://test.pypi.org/simple/ silvasta
```

## Quickstart

### PathGuard

```python
from pathlib import Path
from silvasta import PathGuard

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
from silvasta.config import ConfigManager, SstSettings, SstPaths

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
from silvasta.cli import attach_callback, logger_catch

app = typer.Typer()

@logger_catch
@app.command()
def run():
    ...

attach_callback(app)  # attaches logging, config, printer, verbose/quiet flags
```

## Module Overview

- **`silvasta.utils`** — `PathGuard`, `Printer`, `setup_logging`, `day_count`, ...
- **`silvasta.config`** — `ConfigManager`, `SstSettings`, `SstPaths`, `SstDefaults`, ...
- **`silvasta.cli`** — `attach_callback`, `logger_catch`, `monitor`
- **`silvasta.data`** — File helpers

Full API documentation is available in the docstrings and on GitHub.

## License

Apache License 2.0. See [LICENSE](LICENSE) file.
