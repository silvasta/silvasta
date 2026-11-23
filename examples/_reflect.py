"""
Callable Module Test

⇒  u _reflect.py
_call
_call
None

[(_call)][ 󰂒 ](__name__=_call, __qualname__=_call)
[(_call)][ 󰂒 ]
Functor
Functor
None

[(Functor)][ 󰂒 ](__name__=Functor, __qualname__=Functor)
[(Functor)][ 󰂒 ]

"""

from sstcore.brick import reflect
from sstcore.forge.func import BaseFunctor

functor = BaseFunctor()

print(reflect(functor))
print(reflect.clsname(functor))
print(reflect.attr(functor, "_emit"))
print()
print(repr(functor))
print(str(functor))

functor2 = BaseFunctor(name="Functor")

print(reflect(functor2))
print(reflect.clsname(functor2))
print(reflect.attr(functor2, "_emit"))
print()
print(repr(functor2))
print(str(functor2))
