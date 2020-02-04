import pytest
from liesl.files.labrecorder.cli_wrapper import find_lrcmd, find_lrcmd_os


def test_find_lrcmd_no_path(tmpdir):
    with pytest.raises(FileNotFoundError):
        find_lrcmd(path_to_cmd=str(tmpdir / "sub"))


@pytest.mark.parametrize("platform", ["windows", "linux"])
def test_find_lrcmd_os(platform):
    path = find_lrcmd_os(platform)
    assert path.exists()


def test_find_lrcmd_os_raises():
    with pytest.raises(NotImplementedError):
        find_lrcmd_os("mac")


@pytest.mark.parametrize("platform", ["windows", "linux"])
def test_find_lrcmd(monkeypatch, platform):
    import sys

    monkeypatch.setattr(sys, "platform", platform)
    path = find_lrcmd()
    assert path.exists()


def test_find_lrcmd_raises():
    with pytest.raises(FileNotFoundError):
        find_lrcmd("~")

