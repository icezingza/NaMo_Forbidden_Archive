import importlib
import pytest

@pytest.mark.skipif(importlib.util.find_spec("core") is None, reason="no core package yet")
def test_core_module_exists():
    assert importlib.import_module("core") is not None

@pytest.mark.skipif(importlib.util.find_spec("adapters") is None, reason="no adapters package yet")
def test_adapters_module_exists():
    assert importlib.import_module("adapters") is not None
