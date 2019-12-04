def test_mock_str(mock, capsys):
    print(mock)
    out, err = capsys.readouterr()
    assert "<name>MockEEG</name>" in out
    assert "<type>EEG</type>" in out


def test_markermock_str(markermock, capsys):
    print(markermock)
    out, err = capsys.readouterr()
    assert "<name>MockMarker</name>" in out
    assert "<type>Marker</type>" in out

