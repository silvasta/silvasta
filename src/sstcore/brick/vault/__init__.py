"""
Implement the Variations and Extensions of the Core Registry

The story:
The `Registry` pipeline starts in the port with the root `Register`.
This is the absolute requirement for the `Vaults`
and the plan for everything. The `Vaults` introduce the contracts
and theoretically everything can be built with that.
Final step are the `Registry` assembling and implementations,
like in `error`, `event`, `data.files` and the idea is as well
to assemble and construct some heavy parts in `sstcore.forge`
with the (meta-)builder there and other parts from `brick`.

So far no detailed plans for that,
maybe the intermediate base of the handler registry
if some concepts later on can be generalized and improved there.

All of this as information why it is important not to diverge
too much from the initial plan, not already now,
later on leaf registries should just do their job and be flexible,
they don't need to look like the initial plan but like registries,
solid built thanks to the plan.


                                                 DependencyLevel[1]
"""

__all__: list[str] = [
    "ListVault",
    "TupleVault",
    "DictVault",
    # bases
    "BaseVault",
    "Mapped",
    "Sequential",
    # linear
    "VaultAccess",
    "VaultWriter",
    "VaultReader",
    "VaultContract",
]


from ._access import VaultAccess, VaultReader, VaultWriter
from ._base import BaseVault
from ._contract import VaultContract
from ._mapping import DictVault, Mapped
from ._sequence import ListVault, Sequential, TupleVault
