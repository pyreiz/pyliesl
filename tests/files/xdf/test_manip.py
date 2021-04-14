import pytest
from liesl.files.xdf.manip import find_closest_timestamp_index
from liesl.api import XDFFile
import numpy as np


def test_find_closest_timestamp_index(xdf_file):
    xdf = XDFFile(xdf_file)
    markerstream = xdf["Liesl-Mock-Marker"]
    datastream = xdf["Liesl-Mock-EEG"]
    closest = find_closest_timestamp_index(
        markerstream.time_stamps[0], datastream.time_stamps
    )
    assert type(closest) == int
    delta = markerstream.time_stamps[0] - datastream.time_stamps[closest]
    step = np.mean(np.diff(datastream.time_stamps))
    assert delta < step
