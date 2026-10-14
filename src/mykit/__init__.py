"""MyKit - simplify scientific research workflows."""

import importlib
from importlib.metadata import version
from types import ModuleType

__version__ = version("mykit")

__all__ = []
lazy_modules = ["log"]


def __getattr__(name: str) -> ModuleType:
    """Allow to load a module on import only.

    The classic approch is to define modules in __init__.py. For instance:

        from . import log

    However, we would like modules to be solely imported when they are required, not
    when `mykit` is called. A solution is to use `:func:__getattr__` to initialize a
    module on import only.

    Parameters
    ----------
    name : str
        The name of the module to import.

    Returns
    -------
    ModuleType
        The module to import, if existant.

    Raises
    ------
    AttributeError
        If the module in not present in `lazy_modules`.
    """
    if name not in lazy_modules:
        raise AttributeError(
            f"Module {name} not known. Existing modules are {lazy_modules}"
        )
    return importlib.import_module("." + name, __name__)


def __dir__() -> list[str]:
    """Return the known modules, rather than the project globals.

    By default, __dir__ return the globals for __init__.py. However, modules are not
    defined in __init__.py, but imported on call with `:func:__getattr__`.

    Returns
    -------
    list[str]
        The list of modules, lazy or not.
    """

    return sorted(__all__ + lazy_modules)
