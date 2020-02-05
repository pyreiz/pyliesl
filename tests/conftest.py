from liesl.streams.mock import Mock, MarkerMock
from pytest import fixture


@fixture(scope="session")
def mock():
    mock = Mock()
    mock.await_running()
    yield mock
    mock.stop()


@fixture(scope="session")
def markermock():
    mock = MarkerMock()
    mock.await_running()
    yield mock
    mock.stop()
