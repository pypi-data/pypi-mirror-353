# azt/__init__.py

"""
azt – Collection of tools, functions, and scripts for
data analysis, visualization, machine learning, and more.
"""

__version__ = "0.0.1.pre1"

from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING

def _lazy(name: str) -> ModuleType:
    return import_module(name)

import sys as _sys
_sys.modules[__name__ + ".pandas"] = _lazy("azt.pandas")

__all__ = ["pandas", "__version__"]
if TYPE_CHECKING:      # let editors see symbols for autocompletion
    from azt import pandas  # noqa: F401