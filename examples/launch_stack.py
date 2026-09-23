"""
Launch Stubbed Stack

uv run ~/sstcore/examples/launch_stack.py

"""

from sstcore.brick.stack import DTO_STACK as dto1  # noqa:N811

x = dto1.key11("hello")

result = dto1.key11.key32.key21("Hans")
test = dto1.key21.key13.key31("alice")

print(f"Final: {result=}")
