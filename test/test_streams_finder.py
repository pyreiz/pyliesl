import liesl
from pylsl import StreamInfo, StreamInlet


def test_recover_info():
    pass


def test_find_all(markermock, mock):
    assert len(liesl.get_streaminfos_matching()) == 2


def test_find_selective(markermock, mock):
    assert len(liesl.get_streaminfos_matching(name="MockEEG")) == 1
    assert len(liesl.get_streaminfos_matching(name="MockMarker")) == 1
    assert len(liesl.get_streams_matching(name="MockEEG")) == 1
    assert len(liesl.get_streams_matching(name="MockMarker")) == 1


def test_streams(markermock, mock):
    stream = liesl.open_stream(name="MockEEG")
    sinfo = liesl.open_streaminfo(name="MockEEG")
    assert stream.info().name() == sinfo.name()


def test_sinfo(markermock, mock):
    sinfo = liesl.get_streaminfos_matching(name="MockEEG")[0]
    assert sinfo.name() == "MockEEG"
    sinfo = liesl.get_streaminfos_matching(name="MockMarker")[0]
    assert sinfo.name() == "MockMarker"
