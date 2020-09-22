import pytest
from liesl.api import XDFFile


def test_xdffile_class(xdf_file):
    xdfs = XDFFile(xdf_file)
    assert (
        len(xdfs) == 4
    )  # this is due to a bug on pytest fixtures, which creates two streams each

    key = "Liesl-Mock-EEG"
    xdf = xdfs[key]
    assert xdf.channel_count == 8
    assert xdf.channel_labels[0] == "C001"
    assert xdf.channel_types[0] == "MockEEG"
    assert xdf.channel_units[0] == "au"
    assert xdf.type == "EEG"
    assert xdf.name == key
    assert xdf.channel_format == "float32"
    assert type(xdf.created_at) == float
    assert xdf.time_series.shape[1] == 8
    assert len(xdf.time_stamps.shape) == 1
    assert xdf.nominal_srate == 1000.0
    assert xdf.hostname == xdfs["Liesl-Mock-EEG2"].hostname

