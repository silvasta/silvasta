"""
Launch Stubbed Stack

u ~/sstcore/examples/launch_stack.py

"""

from sstcore.brick import stack

#  LINE: -- Stack -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# class TextProcessor:
#     def __init__(self, color_box):
#         self.sanitize = StackingCore(
#             layers=[sanitizers, normalizers],
#             finalizer=compose,
#         )
#         self.format = StackingCore(
#             layers=[formatters],
#             finalizer=apply_formatters,
#         )
#         self.color = color_box.color  # reuse existing ColorStack
#
#     def process(self, text: str) -> str:
#         text = self.sanitize.strip.html(text)
#         text = self.format.title(text)
#         return self.color.red.bold(text)


#  LINE: -- MulitStackDTO -- -- - -- -- - -- -- - -- -- - -- -- - -- --

multi_stack: stack.MulitStackDTO = stack.MulitStackDTO()


class Handler:
    stack: stack.MulitStackDTO = multi_stack


handler = Handler()

x = handler.stack.key11.key21.key31("Alice")
# dotx = handler.stack.key11.key21


y = handler.stack.key21.key32("Bob")
# doty = handler.stack.key21

z = handler.stack.key13.key33("Charlie")
# dotz = handler.stack
