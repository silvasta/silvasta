# """
# DictRegistry - Main Variation of the Core Registry
#
# -
# """
#
# __all__: list[str] = [
#     "DictRegistry",
# ]
#
# from collections.abc import Iterable
# from typing import TYPE_CHECKING, Any, Unpack
#
# from ...port.register import DictRegister
#
# type D[K,I]=dict[K,I]
#
# class DictRegistry[I, K]:
#     """Implement the Shape of the Registry with Dict"""
#
#     items: D[K, I]
#
#     def __len__(self) -> int:
#         return len(self.items)
#
#
#
#     def add(
#         self, override: bool = False, **items: Unpack[K, I]
#     ) -> list[I]:
#         cleared: dict[K, I] = {}
#         for key, item in items:
#             if override:
#                 cleared.update(self.clear(key))
#             self.items.update(**{key: item})
#         return cleared
#
#     def clear(self, *keys: K) -> dict[K, I]:
#         cleared: dict[K, I] = {}
#         if not keys:
#             self.items.clear()
#         else:
#             for key in keys:
#                 if item := self.items.pop(key, None):
#                     cleared[key] = item
#         return cleared
#
#     def find(self, key: K) -> D[K,I]:
#         return {key:item for ( item:=self.items.pop(key)if item is not None )}
#
#     def __iter__(self) -> Iterable[I]:
#         yield from self.items.values()
#
#     def __contains__(self, target: K) -> bool:
#         return target in self.items
#
#
# if TYPE_CHECKING:
#     _instance: DictRegister = DictRegistry()
#     _class: type[DictRegister] = DictRegistry
