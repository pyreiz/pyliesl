import pytest
from liesl.files.session import Session, Recorder
import time


def test_session_context(tmpdir, mock, markermock):
    streamargs = [{"type": "EEG"}, {"type": "Marker"}]
    session = Session(prefix="VvNn", mainfolder=tmpdir, streamargs=streamargs)
    assert session._is_recording == False
    with session("test"):
        time.sleep(5)
        assert session._is_recording == True
    assert (tmpdir / "VvNn" / "test_R001.xdf").exists()


def test_session_raises(tmpdir, mock, markermock):
    streamargs = [{"type": "EEG"}, {"type": "Marker"}]
    session = Session(
        prefix="VvNn", mainfolder=tmpdir, streamargs=streamargs, recorder=Recorder()
    )
    assert session._is_recording == False
    with session("test"):
        time.sleep(3)
        assert session._is_recording == True
        with pytest.raises(FileExistsError):
            session.start_recording("othertest")
    assert session._is_recording == False

