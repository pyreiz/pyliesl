import pytest
import time
import numpy as np
from numpy.random import random
from liesl.buffers.ringbuffer import SimpleRingBuffer, RingBuffer
from liesl.streams.finder import get_streaminfos_matching


def test_simpleringbuffer():
    rb = SimpleRingBuffer(1000, 2)
    assert rb.shape == (0, 2)
    assert rb.max_column == 2
    assert rb.max_row == 1000
    assert rb.max_shape == (1000, 2)


def test_simpleringbuffer_methods():
    ring = SimpleRingBuffer(1000, 64)
    chunk = random((500, 64))
    ring.put(chunk)
    assert ring.is_full is False
    chunk = random((1000, 64))
    ring.put(chunk)
    out = ring.get()
    assert ring.is_full
    assert np.all((out - chunk) == 0)
    ring.reset()
    assert ring.is_full is False


def test_simpleringbuffer_overflow(capsys):
    chunk = random((2000, 64))
    rb = SimpleRingBuffer(1000, 64, verbose=True)
    rb.put(chunk)
    cs = capsys.readouterr()
    assert "Overflow" in cs.out


def test_simpleringbuffer_speed():
    import time

    ring = SimpleRingBuffer(1000, 64)
    chunk = random((50, 64))
    t0 = time.time()
    dt = []
    for i in range(1000):
        ring.put(chunk)
        t1 = time.time()
        dt.append(t1 - t0)
        t0 = t1
    assert max(dt) < 0.001


@pytest.fixture
def rb(mock):
    sinfo = get_streaminfos_matching(name="Liesl-Mock-EEG")[0]
    rb = RingBuffer(streaminfo=sinfo, duration_in_ms=1000)
    rb.await_running()
    yield rb
    rb.stop()


def test_ringbuffer_properties(rb):
    time.sleep(2)
    assert rb.is_running == True
    assert rb.is_full == True
    rb.reset()
    assert rb.is_full == False


def test_ringbuffer_methods(rb):
    time.sleep(1)
    rb.stop()
    chunk, tstamps = rb.get()
    chunk2 = rb.get_data()
    assert np.round(np.median(np.diff(tstamps[:, 0])), 3) == 0.001
    assert np.all((chunk - chunk2) == 0)


def test_ringbuffer(mock):
    sinfo = get_streaminfos_matching(name="Liesl-Mock-EEG")[0]
    rb = RingBuffer(streaminfo=sinfo, duration_in_ms=1000)
    assert rb.fs == 1000
    assert rb.max_shape == (1000, 8)
    assert rb.shape == (0, 8)

