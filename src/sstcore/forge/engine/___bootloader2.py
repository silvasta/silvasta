"""
Boot subclasses from root class

- Part2: with config

"""

from typing import Any


class StableBase:
    """The stable core used across many projects."""

    def core_utility(self):
        return "System checked."


class ProjectLocalBase(StableBase):
    """The firebreak. Only classes for THIS project inherit from here."""

    @classmethod
    def boot_all(cls, full_config=None) -> list[ProjectLocalBase]:
        full_config: dict[str, Any] = full_config or {}
        instances = []

        for sub_cls in cls.__subclasses__():
            # 1. Look for config matching the class name (e.g., 'DataFetcher')
            # 2. Default to an empty dict if no specific config is provided
            class_specific_kwargs = full_config.get(sub_cls.__name__, {})

            # 3. Unpack those specific settings into the new instance
            worker = sub_cls(**class_specific_kwargs)
            instances.append(worker)
        return instances

    def execute(self):
        """To be overridden by the 10 child classes."""
        raise NotImplementedError("Subclasses must implement execute()")


class DataFetcher(ProjectLocalBase):
    # Expects specific instance variables
    def __init__(self, endpoint="http://default.api", timeout=30):
        self.endpoint = endpoint
        self.timeout = timeout

    def execute(self):
        print(f"Fetching from {self.endpoint} with {self.timeout}s timeout.")


class DatabaseWriter(ProjectLocalBase):
    def __init__(self, table_name="temp_data"):
        self.table_name = table_name

    def execute(self):
        print(f"Writing to table: {self.table_name}")


class DataParser(ProjectLocalBase):
    def execute(self):
        print("Parsing data...")


app_config = {
    "DataFetcher": {
        "endpoint": "https://api.myproject.com/v1",
        "timeout": 60,
    },
    "DatabaseWriter": {
        "table_name": "production_metrics",
    },
    # Note: If we added a DataParser class but left it out of
    # this dictionary, it safely falls back to its own defaults.
}

# Boot all workers, injecting their specific states
active_workers = ProjectLocalBase.boot_all(app_config)

for worker in active_workers:
    worker.execute()
