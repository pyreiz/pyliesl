from liesl.streams.mock import Mock, MarkerMock
from pytest import fixture


@fixture
def mock():
    mock = Mock()
    mock.start()
    yield mock
    mock.stop()


def test_mock_creation(mock):
    pass
