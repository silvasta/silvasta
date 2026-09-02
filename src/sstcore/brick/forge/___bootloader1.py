"""
Boot subclasses from root class

- Part1: just boot

"""


class StableBase:
    """The stable core used across many projects."""

    def core_utility(self):
        return "System checked."


class ProjectLocalBase(StableBase):
    """The firebreak. Only classes for THIS project inherit from here."""

    @classmethod
    def boot_all(cls) -> list[ProjectLocalBase]:
        """Detects, instantiates, and returns all local workers."""
        instances = []

        # Detect all direct subclasses of ProjectLocalBase
        for sub_cls in cls.__subclasses__():
            # Initialize them (assuming they require no arguments)
            worker = sub_cls()
            instances.append(worker)

        return instances

    def execute(self):
        """To be overridden by the 10 child classes."""
        raise NotImplementedError("Subclasses must implement execute()")


class DataFetcher(ProjectLocalBase):
    def execute(self):
        print("1. Fetching data...")


class DataParser(ProjectLocalBase):
    def execute(self):
        print("2. Parsing data...")


class DatabaseWriter(ProjectLocalBase):
    def execute(self):
        print("3. Writing to database...")


active_workers = ProjectLocalBase.boot_all()

# Steer them
for worker in active_workers:
    # They all inherit core utilities from StableBase
    print(worker.core_utility())

    # And they all execute their local logic
    worker.execute()
