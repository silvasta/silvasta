"""
Launch Stack internally

um sstcore.brick.stack._example

"""

from . import _stack_dto as stack

#  LINE: -- Stack -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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
