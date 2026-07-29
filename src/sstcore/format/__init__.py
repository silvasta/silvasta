"""
Preprocess the Input of preferably Leaf Packages (like exceptions)

- Decouple from Utils to prevent Dependency Issues at all costs

                                                          PackageLevel[1]
"""

from ._normalize import cls_name

__all__: list[str] = [
    "cls_name",
]
