import liesl
import socket
from pylsl import StreamInfo, StreamInlet
import pytest


def test_find_all(markermock, mock):
    assert len(liesl.get_streaminfos_matching()) == 2


def test_find_selective(markermock, mock):
    assert len(liesl.get_streaminfos_matching(name="Liesl-Mock-EEG")) == 1
    assert len(liesl.get_streaminfos_matching(name="Liesl-Mock-Marker")) == 1
    assert len(liesl.get_streams_matching(name="Liesl-Mock-EEG")) == 1
    assert len(liesl.get_streams_matching(name="Liesl-Mock-Marker")) == 1
    assert liesl.get_streams_matching(name="notexisting") == None
    assert liesl.get_streaminfos_matching(name="notexisting") == None


def test_open_streams(markermock, mock):
    stream = liesl.open_stream(name="Liesl-Mock-EEG")
    sinfo = liesl.open_streaminfo(name="Liesl-Mock-EEG")
    assert stream.info().name() == sinfo.name()


def test_open_streams_fringe_cases(markermock, mock):
    assert liesl.open_stream(name="notexistent") == None
    assert liesl.open_streaminfo(name="notexistent") == None
    with pytest.raises(ConnectionError):
        liesl.open_streaminfo(hostname=socket.gethostname())
    with pytest.raises(ConnectionError):
        liesl.open_stream(hostname=socket.gethostname())


def test_recover_info(markermock, mock):
    stream = liesl.open_stream(name="Liesl-Mock-EEG")
    sinfo = liesl.streams.finder.recover_info(stream)
    assert stream.info().name() == sinfo.name()


def test_print_available_streams(markermock, mock, capsys):
    out, err = capsys.readouterr()
    liesl.print_available_streams()
    out, err = capsys.readouterr()
    assert "<name>Liesl-Mock-EEG</name>" in out
    assert "<name>Liesl-Mock-Marker</name>" in out


def test_sinfo(markermock, mock):
    sinfo = liesl.get_streaminfos_matching(name="Liesl-Mock-EEG")[0]
    assert sinfo.name() == "Liesl-Mock-EEG"
    sinfo = liesl.get_streaminfos_matching(name="Liesl-Mock-Marker")[0]
    assert sinfo.name() == "Liesl-Mock-Marker"

