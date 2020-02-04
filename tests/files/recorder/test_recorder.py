import pytest
from liesl.files.labrecorder.cli_wrapper import find_lrcmd, find_lrcmd_os
from liesl.files.labrecorder.cli_wrapper import LabRecorderCLI
import time


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


def test_labrecorder(mock, markermock, tmpdir):
    lr = LabRecorderCLI()
    # from pathlib import Path
    # tmpdir = Path("~/Desktop").expanduser()
    filename = tmpdir / "test.xdf"
    streamargs = [{"type": "EEG"}, {"type": "Marker"}]
    filename = lr.start_recording(filename, streamargs)
    time.sleep(3)
    lr.stop_recording()
    assert filename.exists()
    if filename.exists():
        filename.unlink()


def test_labrecorder_no_streams(tmpdir):
    lr = LabRecorderCLI()
    filename = tmpdir / "test.xdf"
    with pytest.raises(ValueError):
        lr.start_recording(filename)


def test_labrecorder_no_streams_found(tmpdir):
    lr = LabRecorderCLI()
    filename = tmpdir / "test.xdf"
    streamargs = [{"name": "not-available"}]
    with pytest.raises(ConnectionError):
        lr.start_recording(filename, streamargs)

