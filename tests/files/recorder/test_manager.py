from liesl.files.labrecorder.manager import *
import pytest


def test_validate(mock, markermock):
    sids = validate([{"name": "Liesl-Mock-EEG"}, {"name": "Liesl-Mock-Marker"}])


def test_validate_raises(mock, markermock):
    with pytest.raises(ConnectionError):
        sids = validate([{"name": "Liesl-Mock-EEG"}, {"name": "not-available"}])
    with pytest.raises(ConnectionError):
        sids = validate([{"name": "Liesl-Mock-EEG"}, {"name": "Liesl-Mock-EEG"}])


def test_add_to_path():
    pass


def test_follow_lnk():
    pass


@pytest.mark.parametrize("fname", ["test.txt", "LabRecorderCLI.exe"])
def test_find_file(tmpdir, fname):
    p = tmpdir.mkdir("sub").join(fname)
    p.write("content")
    find_file(path=str(tmpdir), file=fname)
