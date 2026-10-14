"""MyKit - simplify scientific research workflows."""

import importlib as _importlib
from importlib.metadata import PackageNotFoundError as _PackageNotFoundError
from importlib.metadata import version as _version
from types import ModuleType as _ModuleType

try:
    __version__ = _version("mykit")
except _PackageNotFoundError:  # if running from sources rather than installed
    __version__ = "0+unknown"

_DOMAINS = frozenset({"log"})
__all__ = sorted(_DOMAINS)


def __getattr__(name: str) -> _ModuleType:
    """Allow to load a module on first-access.

    The classic approach is to define modules in __init__.py. For instance:

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
        The module to import, if it exists.

    Raises
    ------
    AttributeError
        If the module is not present in `_DOMAINS`.
    """
    if name not in _DOMAINS:
        raise AttributeError(f"module 'mykit' has no attribute {name!r}")
    return _importlib.import_module("." + name, __name__)


def __dir__() -> list[str]:
    """Return the known modules, rather than the project globals.

    By default, __dir__ return the globals for __init__.py. However, modules are not
    defined in __init__.py, but imported on call with `:func:__getattr__`.

    Returns
    -------
    list[str]
        The list of modules, lazy or not.
    """

    return sorted(set(globals()) | _DOMAINS)
