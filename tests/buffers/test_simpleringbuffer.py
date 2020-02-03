from liesl.buffers.ringbuffer import SimpleRingBuffer
from numpy.random import random
import numpy as np


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
