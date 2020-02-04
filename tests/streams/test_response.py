import pytest
from liesl.streams.response import Response, MockResponse
import numpy as np
import json

idx = 500


@pytest.fixture
def rsp():
    yield MockResponse()


def test_response_init_raises():
    tstamps = np.linspace(0, 1, 1001)
    chunk = np.arange(0, 1000, dtype=float)
    onset_in_ms = tstamps[idx]
    with pytest.raises(ValueError):
        Response(
            chunk=chunk,
            tstamps=tstamps,
            onset_in_ms=onset_in_ms,
            fs=1000,
            pre_in_ms=50,
            post_in_ms=50,
            ep_window_in_ms=[15, 50],
        )


def test_response_properties(rsp):
    assert rsp.onset == idx
    assert rsp.pre == idx - 50
    assert rsp.post == idx + 50
    assert rsp.ep_window == [idx + 15, idx + 50]


def test_response_get_latency(rsp):
    assert rsp.get_latency() == [15.0, 50.0]


def test_response_trace(rsp):
    trace = rsp.get_trace(channel_idx=0, baseline_correction=True)
    assert trace[50] == 25.0
    trace = rsp.get_trace(channel_idx=0, baseline_correction=False)
    assert trace[50] == 500.0


def test_response_vpp(rsp):
    assert rsp.get_vpp() == 50 - 15


@pytest.mark.parametrize("stepsize", [0.5, 1.0, 5.0])
def test_response_xaxis(rsp, stepsize):
    xticks, xticklabels, xlim = rsp.get_xaxis(stepsize=stepsize)
    assert np.all(np.diff(xticks) == stepsize)
    assert xticklabels[0] == "-50"
    assert xticklabels[-1] == "50"
    assert xlim == (0, 100)


def test_response_xaxis_raises(rsp):
    with pytest.raises(ValueError):
        xticks, xticklabels, xlim = rsp.get_xaxis(stepsize=-1)


@pytest.mark.parametrize(
    "key, value",
    [("mepmaxtime", 15.0), ("mepamplitude", 35.0), ("mepmin", 40.0), ("mepmax", 75.0)],
)
def test_response_as_json(rsp, key, value):
    d = json.loads(rsp.as_json())
    assert d[key] == value

