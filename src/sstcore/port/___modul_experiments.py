import importlib.machinery
import importlib.util
import sys
import types

#  LINE: -- Dynamic Execution -- -- - -- -- - -- -- - -- -- - -- -- - -- --

my_mod = types.ModuleType("dynamic_math")

# Attach documentation and attributes
my_mod.__doc__ = "A dynamically generated math helper."
my_mod.PI = 3.14159  # ty:ignore


def add(a, b):
    return a + b


my_mod.add = add  # ty:ignore


#  LINE: -- Dynamic Execution -- -- - -- -- - -- -- - -- -- - -- -- - -- --


print(my_mod.PI)  # 3.14159
print(my_mod.add(5, 7))  # 12

code_str = """
def greet(name: str) -> str:
    return f"Hello, {name}!"

MESSAGE = "Dynamic module loaded."
"""

dynamic_mod = types.ModuleType("greeter")

exec(code_str, dynamic_mod.__dict__)  # CHECK:

print(f"{dynamic_mod.MESSAGE=}")
print(f"{dynamic_mod.greet("Alice")=}")

module_name = "in_memory_config"


#  LINE: -- Dynamic Memory -- -- - -- -- - -- -- - -- -- - -- -- - -- --


spec: importlib.machinery.ModuleSpec | None = importlib.util.spec_from_loader(
    module_name, loader=None
)
config_mod: types.ModuleType = importlib.util.module_from_spec(spec)  # ty:ignore

# Populate attributes
config_mod.DEBUG = True  # ty:ignore
config_mod.ENV = "production"  # ty:ignore

# Register into sys.modules
sys.modules[module_name] = config_mod

# Now it can be imported anywhere in the runtime
import in_memory_config  # ty:ignore #noqa:E402

print(f"{in_memory_config.DEBUG=}")  # True
