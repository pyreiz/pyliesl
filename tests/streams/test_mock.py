def test_mock_str(mock, capsys):
    print(mock)
    out, err = capsys.readouterr()
    assert "<name>Liesl-Mock-EEG</name>" in out
    assert "<type>EEG</type>" in out


def test_markermock_str(markermock, capsys):
    print(markermock)
    out, err = capsys.readouterr()
    assert "<name>Liesl-Mock-Marker</name>" in out
    assert "<type>Marker</type>" in out


def test_desclessmock(desclessmock, capsys):
    print(desclessmock)
    out, err = capsys.readouterr()
    assert "<name>Liesl-Descless-Mock</name>" in out
    assert "<type>EEG</type>" in out

