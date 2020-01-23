import liesl.api as liesl


def test_convert_inlet_to_dict(mock):
    stream = liesl.open_stream(name="Liesl-Mock-EEG")
    sdict = liesl.inlet_to_dict(stream)
    assert "name" in sdict.keys()
    assert sdict["name"] == "Liesl-Mock-EEG"
    labels = liesl.inlet_to_chanidx(stream)
    assert labels["C001"] == 0
    assert len(labels) == 8
