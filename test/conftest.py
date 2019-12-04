from liesl.streams.mock import Mock, MarkerMock
from pytest import fixture


@fixture(scope="session")
def mock():
    mock = Mock()
    yield mock
    mock.stop()
    # out, err = capsys.readouterr()
    # assert "Shutting down" in out
