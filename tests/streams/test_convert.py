import liesl.api as liesl


def test_inlet_to_dict(mock):
    stream = liesl.open_stream(name="Liesl-Mock-EEG")
    sdict = liesl.inlet_to_dict(stream)
    assert "name" in sdict.keys()
    assert sdict["name"] == "Liesl-Mock-EEG"


def test_get_channel_map(mock):
    stream = liesl.open_stream(name="Liesl-Mock-EEG")
    labels = liesl.get_channel_map(stream)
    assert labels["C001"] == 0
    assert len(labels) == 8
