def test_mock_creation(mock, capsys):
    mock.start()
    out, err = capsys.readouterr()
    assert "now sending data...\n" in out


def test_mock_str(mock, capsys):
    print(mock)
    out, err = capsys.readouterr()
    assert (
        '<?xml version="1.0"?>\n<info>\n\t<name>MockEEG</name>\n\t<type>EEG</type>'
        in out
    )

