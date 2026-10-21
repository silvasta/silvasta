# Base of all Projects — `sstcore`

[![PyPI version](https://img.shields.io/pypi/v/sstcore-py.svg)](https://pypi.org/project/sstcore-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/sstcore-py.svg)](https://pypi.org/project/sstcore-py/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**Generalize Project Patterns and Bootstrap with Batteries.**

`sstcore` (distributed on PyPI as `sstcore-py`) is a strictly layered Python architecture and utility framework (`>=3.14`). It serves as the foundation across projects by uniting configuration bootstrapping, structured console output, event buses, CLI/TUI pipelines, and filesystem safety behind a lazy-loaded root facade.

---

## Installation

> **Note:** The PyPI distribution name is **`sstcore-py`**, while the Python import module is **`sstcore`**.

```bash
# Core library (System, ConfigManager, PathGuard, printer, EmitCore, portlink)
uv add sstcore-py

# Recommended: includes Typer + Textual for SafeTyper and the `sst` CLI tools
uv add "sstcore-py[cli]"

# With all optional extras
uv add "sstcore-py[all]"
```

**Install from TestPyPI:**

<!-- TODO: remove this for (not test) pypi -->

```bash
uv add \
  --index https://test.pypi.org/simple/ \
  --default-index https://pypi.org/simple/ \
  --index-strategy unsafe-best-match \
  "sstcore-py[all]"
```

---

## Built-in CLI Suite (`sst`)

When installed with `[cli]` or `[all]`, `sstcore` provides the standalone **`sst`** terminal command powered by `SafeTyper` and `Textual`:

```bash
sst --help
```

- **`sst scanner`** — Interactive TUI file-tree selector: scan a folder, cherry-pick files in the terminal UI, and merge them into a single summary artifact.
- **`sst monitor`** — Live-updating log console monitoring log files and `.jsonl` streams in real time.
- **`sst print`** — Render and format Markdown files directly in the terminal via `Rich`.

---

## Root Facade & Examples

All primary framework entry points are exposed directly on `sstcore` via lazy loading (`__getattr__`):

```python
from sstcore import (
    System,
    EmitCore,
    printer,
    ConfigManager,
    SafeTyper,
    PathGuard,
    portlink,
)
```

### 1. `System` — Command & Control Central

Unites `ConfigManager`, `printer`, and the event bus to bootstrap and distribute application state.

```python
from sstcore import System

# TODO: Add v0.4.0 System bootstrap example
```

### 2. `EmitCore` — Ergonomic Event Facade

Launch and subscribe to system-wide events from a decoupled facade.

```python
from sstcore import EmitCore

# TODO: Add v0.4.0 EmitCore event emission example
```

### 3. `printer` — Fast Terminal Visualization

Structured console output, color boxes, and Rich-powered formatting (`Paint -> Printer -> Canvas -> CLI`).

```python
from sstcore import printer

# TODO: Add v0.4.0 printer example (e.g., printer.danger, canvas/color usage)
```

### 4. `ConfigManager` — Configuration & Bootstrap Family

Pydantic-based settings management (`pydantic` + `pydantic-settings`), home directory setup, and `.env` loading.

```python
from sstcore import ConfigManager

# TODO: Update v0.4.0 ConfigManager bootstrap & settings access example
```

### 5. `SafeTyper` — CLI Pipeline with Defaults

Seamless CLI execution pipeline wrapping `Typer` with automatic error boundaries, logging callbacks, and system wiring. _(Requires `sstcore-py[cli]`)_

```python
from sstcore import SafeTyper

# TODO: Add v0.4.0 SafeTyper app & command example
```

### 6. `PathGuard` — Fail-Safe Filesystem & Path Management

Hybrid decorator and function API for safe path handling, automatic directory creation, unique file sequences, rotation, pruning, and safe deletion (`send2trash`).

```python
from pathlib import Path
from sstcore import PathGuard

# TODO: Verify/update PathGuard v0.4.0 API signatures
# log_dir = PathGuard.dir("~/logs/myapp")
# PathGuard.rotate("old_data", "archive/data_v1")
# PathGuard.prune("backups/model_", remaining=5)
```

### 7. `portlink` — Architectural Contract Linking

Decoupled contract and dependency linking across strictly separated package layers.

```python
from sstcore import portlink

# TODO: Add v0.4.0 portlink usage example
```

---

## Architecture: The L0–L6 Layer Model

`sstcore` enforces a strict bottom-up dependency graph. Each top-level package occupies an isolated dependency tier where imports only flow upward:

| Tier   | Package           | Responsibility                                                                             |
| :----- | :---------------- | :----------------------------------------------------------------------------------------- |
| **L6** | `sstcore.console` | Main interface and execution (`cli`, `tui`, `select`, `tools`, `SafeTyper`)                |
| **L5** | `sstcore.system`  | Command and control central (`boot`, `config`, `event`, `globals`, `System`)               |
| **L5** | `sstcore.data`    | Intermediate support layer, models, and file handling                                      |
| **L4** | `sstcore.util`    | Structured helpers (`path`, `print`, `log`, `parse`, `filter`, `scan`, `tree`, `write`)    |
| **L3** | `sstcore.error`   | Exception hierarchy, handlers (`catch`), and `raiser`                                      |
| **L2** | `sstcore.forge`   | Shape, compose, and assemble (`compose`, `engine`, `func`, `labor`, `typed`, `view`)       |
| **L1** | `sstcore.brick`   | Universal building blocks (`call`, `color`, `field`, `format`, `reflect`, `time`, `vault`) |
| **L0** | `sstcore.port`    | Pure contracts, protocols, types, and `portlink` definitions                               |

### Dependency Invariants

- **Unified Package Boundary:** A package and its subpackages act as a single module from the outside and share the same external dependency level.
- **Relative Internal Levels:** Internally, the dependency level resets to `0` and bumps by `+1` with every import (consistently bumping export locations as well).
- **`__init__` Ceiling:** A package's `__init__.py` always holds the highest internal dependency level (`DependencyLevel[X]`), representing the entire package to outside consumers.

---

## Repository Branch System & Scratchpad Rules

Development follows a three-tier branch promotion model enforced by `ruff` and `ty`:

- **`main` (Release Tier):** Clean, publish-ready state (1 squash commit per release or major milestone). Zero `ty` type-checker errors allowed. All `___NAME.py` and `____NAME.py` scratchpad files are strictly forbidden.
- **`core` (History & Condenser Tier):** Pre-cleaned history tracker (~5–10 commits per `main` commit). Preserves architectural evolution and `___NAME.py` idea/todo scratchpads (verified by `ruff`), while rejecting `____NAME.py` experimental files.
- **`latest` / Outer Branches (Active Workspace):** Unconstrained development. Allows `____NAME.py` experimental/out-of-service files (ignored by `ruff` and `ty`) to keep rough ideas and unsafe states close to the code.

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
