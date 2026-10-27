"""
Error handling

.
"""

from collections.abc import Generator
from contextlib import contextmanager
from functools import wraps
from typing import Self

from sstcore.util._quick._names import GetNames


class BaseScopedService:
    def __init__(self):
        self._is_active = False

    def __enter__(self):
        self._is_active = True
        self._on_enter()
        return self

    def __exit__(self, _type, error, _tb):
        print(f"Enter __exit__: {self}")
        try:
            return self._on_exit(error)
        finally:
            self._is_active = False

    def _on_enter(self):
        pass

    def _on_exit(self, error):
        print(error)
        return False


class InactiveScopeError(RuntimeError): ...


def require_active(method):

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self._is_active:
            raise InactiveScopeError(
                f"Cannot call '{method.__name__}' outside of an active 'with' block."
            )
        return method(self, *args, **kwargs)

    return wrapper


class DataProcessor(BaseScopedService):
    @require_active
    def process_batch(self, batch):
        # Guaranteed to be within the active lifecycle
        ...

    def data_extraction(self, data) -> list[int]:
        with self:
            return [1, 1] if data else [0, 0]


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class BaseWorker:
    @contextmanager
    def _lifecycle_boundary(self) -> Generator[None]:
        self._setup_guard()
        try:
            yield
        except Exception as error:
            self._on_failure(error)
            raise
        finally:
            self._teardown_guard()

    def _setup_guard(self):
        pass

    def _on_failure(self, error: Exception):
        pass

    def _teardown_guard(self):
        pass


def safe_action(method):

    @wraps(method)
    def wrapper(self: BaseWorker, *args, **kwargs):
        with self._lifecycle_boundary():
            return method(self, *args, **kwargs)

    return wrapper


class PipelineWorker(BaseWorker):
    @safe_action
    def execute_step(self, data): ...


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class MultiWorker(BaseWorker):
    def __init__(self):
        self._active_depth = 0

    def __enter__(self):
        if self._active_depth == 0:
            self._setup_guard()  # Only run on the VERY FIRST enter
        self._active_depth += 1
        return self

    def __exit__(self, _type, error, _tb):
        self._active_depth -= 1
        if self._active_depth == 0:
            self._teardown_guard()  # Only run on the VERY LAST exit
        print(error)
        return False


class MultiBaseWorker:
    @contextmanager
    def protect(self) -> Generator[None]:
        self._setup_guard()
        try:
            yield
        except Exception as error:
            self._on_failure(error)
            raise
        finally:
            self._teardown_guard()

    def __enter__(self):
        return self

    def __exit__(self, _type, error, _tb):
        if _type is None:
            return True
        self._on_failure(error)

    def _setup_guard(self):
        pass

    def _on_failure(self, error: Exception):
        pass

    def _teardown_guard(self):
        pass


def safe(method):

    @wraps(method)
    def wrapper(self: MultiBaseWorker, *args, **kwargs):
        # NOTE: handle multiple __enter__ before usage
        with self:
            return method(self, *args, **kwargs)

    return wrapper


def protect(method):

    @wraps(method)
    def wrapper(self: MultiBaseWorker, *args, **kwargs):
        with self.protect():
            return method(self, *args, **kwargs)

    return wrapper


class Worker(MultiBaseWorker):
    @safe
    def execute_step(self, data): ...
    @protect
    def execute_next(self, data): ...


def tests():
    worker = Worker()
    with worker:
        ...


def clean_pipeline(data):
    worker = Worker()
    worker.execute_next(data)
    processor = DataProcessor()
    x = processor.data_extraction(data)
    print(x)


#  LINE: -- Lap 2 -- -- - -- -- - -- -- - -- -- - -- -- - -- --

get_name = GetNames()


class _DataProcessor(BaseScopedService):
    def __init__(self):
        super().__init__()
        self.options = {}
        self.name = get_name()

    def __str__(self):
        return f"{type(self).__name__}[{self.name}]"

    def clone(self, **options) -> Self:
        cloned: Self = type(self)()
        cloned.options.update(options)
        return cloned

    def __call__(self, **options):
        # AI: what about returning a copy?
        return self.clone(**options)

    def prepare(self):
        print(f"Start to prepare: {self}")

    def execute(self):
        self.prepare()
        for x in range(self.options.get("repeats", 0)):
            print(f"{self} executes... run: {x}")

    def _on_exit(self, _type, error, _tb):  # ty:ignore
        print(f"Enter _on_exit: {self}")
        if _type is None:
            return True
        if issubclass(_type, TypeError):
            print(f"Caught: [{_type.__name__}] {error}")
            return True
        return False

    def fail(self):
        raise AttributeError("fail test")


def safe_debug(*workers):
    for i, w in enumerate(workers, start=1):
        try:
            print(f"Worker {i}: {w}")
        except Exception:
            pass


def _tests():
    worker = _DataProcessor()

    safe_debug(worker)

    # good example
    with worker(repeats=3) as w1:
        w1.execute()

    safe_debug(worker, w1)

    # bad example
    with worker(repeats="3") as w2:
        w2.execute()

    safe_debug(worker, w1, w2)

    worker.prepare()
    w1.prepare()
    w2.prepare()

    try:
        with worker(repeats="3") as w3:
            w3.fail()
    except Exception as error:
        print(f"Caught: [{type(error).__name__}] {error}")

    safe_debug(worker, w1, w2, w3)
    w3.prepare()


if __name__ == "__main__":
    _tests()
