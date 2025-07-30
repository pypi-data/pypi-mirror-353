# Authors: Benjamin Vial
# This file is part of pytmod
# License: GPLv3
# See the documentation at bvial.info/pytmod



# import numdiff as nd
# nd.set_log_level("DEBUG")
# nd.print_info()

# nd.has_torch()
# nd.set_backend("torch")


import pytest


def test_backend():
    import numdiff as nd

    assert nd.get_backend() == "numpy"
    assert nd.BACKEND == "numpy"

    nd.set_backend("scipy")
    assert nd.numpy.__name__ == "numpy"
    assert nd.backend.__name__ == "numpy"
    assert nd.get_backend() == "scipy"
    assert nd.BACKEND == "scipy"

    nd.set_backend("autograd")
    assert nd.numpy.__name__ == "autograd.numpy"
    assert nd.backend.__name__ == "autograd.numpy"
    assert nd.get_backend() == "autograd"
    assert nd.BACKEND == "autograd"

    if nd.has_jax():
        nd.set_backend("jax")
        assert nd.numpy.__name__ == "jax.numpy"
        assert nd.backend.__name__ == "jax.numpy"
        assert nd.get_backend() == "jax"
        assert nd.BACKEND == "jax"

    if nd.has_torch():
        nd.set_backend("torch")
        assert nd.numpy.__name__ == "numpy"
        assert nd.get_backend() == "torch"
        assert nd.backend.__name__ == "torch"
        assert nd.BACKEND == "torch"

    with pytest.raises(ValueError) as excinfo:
        nd.set_backend("fake")
    assert "Unknown backend" in str(excinfo.value)
    nd.set_backend("numpy")
    assert nd.numpy.__name__ == "numpy"
    assert nd.backend.__name__ == "numpy"
    assert nd.get_backend() == "numpy"
    assert nd.BACKEND == "numpy"


def test_notorch(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "torch", None)
    import numdiff

    numdiff.set_backend("torch")

    numdiff.use_gpu(True)
    numdiff.use_gpu(False)


def test_gpu(monkeypatch):
    import numdiff

    numdiff.set_backend("torch")
    numdiff.use_gpu(True)
    numdiff.use_gpu(False)
