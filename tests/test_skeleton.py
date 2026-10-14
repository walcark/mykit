"""Check the package skeleton: lazy imports, domains listing, etc."""

from __future__ import annotations

import subprocess
import sys

import pytest


def _run(code: str) -> None:
    """Run *code* in a fresh interpreter, so that imports start from nothing."""
    subprocess.run([sys.executable, "-c", code], check=True)


def test_import_is_light():
    """`import mykit` loads none of the heavy scientific libraries."""
    _run(
        "import sys, mykit\n"
        "heavy = {'pandas', 'xarray', 'matplotlib', 'torch', 'dask'}\n"
        "loaded = sorted(heavy & {m.split('.')[0] for m in sys.modules})\n"
        "assert not loaded, loaded"
    )


def test_domains_load_on_first_access():
    """A domain is not imported by `import mykit`, only when it is used."""
    _run(
        "import sys, mykit\n"
        "assert 'mykit.log' not in sys.modules\n"
        "mykit.log\n"
        "assert 'mykit.log' in sys.modules"
    )


def test_unknown_attribute_raises():
    import mykit

    with pytest.raises(AttributeError, match="does_not_exist"):
        mykit.does_not_exist  # noqa: B018


def test_domains_are_listed():
    """Tab completion shows the domains, even before they are loaded."""
    import mykit

    assert "log" in dir(mykit)


def test_version_comes_from_the_installed_metadata():
    """One place declares the version: pyproject.toml."""
    from importlib.metadata import version

    import mykit

    assert mykit.__version__ == version("mykit")
