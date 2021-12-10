from liesl.streams.mock import Mock, MarkerMock
from pytest import fixture
from liesl.files.labrecorder.cli_wrapper import LabRecorderCLI
import time


@fixture(scope="session")
def mock():
    mock = Mock()
    mock.await_running()
    yield mock
    mock.stop()


@fixture(scope="session")
def markermock():
    mock = MarkerMock(verbose=False)
    mock.await_running()
    yield mock
    mock.stop()


@fixture(scope="session")
def xdf_file(mock, markermock, tmpdir_factory):
    lr = LabRecorderCLI()
    fn = tmpdir_factory.mktemp("data")
    filename = fn / "test.xdf"
    streamargs = [{"type": "EEG"}, {"type": "Marker"}]
    filename = lr.start_recording(filename, streamargs)
    time.sleep(3)
    lr.stop_recording()
    yield filename
    filename.unlink()
