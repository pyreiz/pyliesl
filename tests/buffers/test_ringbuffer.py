from liesl.buffers.threads import RingBuffer
from liesl.streams.finder import get_streaminfos_matching
import pytest
import time
import numpy as np


@pytest.fixture
def rb(mock):
    sinfo = get_streaminfos_matching(name="Liesl-Mock-EEG")[0]
    rb = RingBuffer(streaminfo=sinfo, duration_in_ms=1000)
    rb.await_running()
    yield rb
    rb.stop()


def test_ringbuffer_properties(rb):
    time.sleep(1)
    assert rb.is_running == True
    assert rb.is_full == True
    rb.reset()
    assert rb.is_full == False


def test_ringbuffer_methods(rb):
    time.sleep(1)
    rb.stop()
    chunk, tstamps = rb.get()
    chunk2 = rb.get_data()
    assert np.round(np.median(np.diff(tstamps[:, 0])), 2) == 0.01
    assert np.all((chunk - chunk2) == 0)


def test_ringbuffer(mock):
    sinfo = get_streaminfos_matching(name="Liesl-Mock-EEG")[0]
    rb = RingBuffer(streaminfo=sinfo, duration_in_ms=1000)
    assert rb.fs == 100
    assert rb.max_shape == (100, 8)
    assert rb.shape == (0, 8)

