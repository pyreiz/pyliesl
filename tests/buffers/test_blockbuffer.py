from liesl.buffers.blockbuffer import SimpleBlockBuffer
import numpy as np


def test_simpleblockbufer():
    blockbuffer = SimpleBlockBuffer(50, 64)
    expected = [False, False, True, False]
    received = []
    for i in range(0, 4, 1):
        chunk = np.random.random((25, 64))
        blockbuffer.handle_chunk(chunk)
        block = blockbuffer.get()
        if block is not None:
            print("Gotcha")
            received.append(True)
        else:
            print("Nada")
            received.append(False)
    assert all([e == r for e, r in zip(expected, received)])


def test_simpleblockbuffer_methods():
    blockbuffer = SimpleBlockBuffer(50, 1)
    chunk = np.arange(0, 200)
    blockbuffer.handle_chunk(chunk)
    block0A = blockbuffer.get()
    assert block0A[0] == 0
    assert block0A.shape == (50, 1)
    block0B = blockbuffer.get_last()
    assert np.all((block0A - block0B) == 0)
    block = blockbuffer.get()
    assert block[0] == 50
