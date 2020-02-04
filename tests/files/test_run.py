import pytest
from liesl.api import Run


@pytest.mark.parametrize("seed", ["test", "test.xdf", "äfvsr-sg_"])
def test_run_creation(tmpdir, seed):
    fname = str(tmpdir / seed)
    run = Run(fname)
    assert run.name == seed.split(".xdf")[0] + "_R001.xdf"
    run.write_text("")  # create the file
    run = Run(fname)  # should increase count
    assert run.name == seed.split(".xdf")[0] + "_R002.xdf"


def test_run_raises():
    with pytest.raises(ValueError):
        Run("test.ini")
