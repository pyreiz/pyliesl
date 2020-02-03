liesl API
----------

The main API can be accessed directly from liesl, e.g.

.. code-block:: python

    import liesl
    stream = liesl.open_stream(name="Liesl-Mock-EEG")

.. automodule:: liesl.streams.finder
   :members: open_stream, open_streaminfo, print_available_streams, get_streams_matching, get_streaminfos_matching

.. automodule:: liesl.streams.convert
   :members: inlet_to_dict, inlet_to_chanidx

.. automodule:: liesl.buffers.ringbuffer
   :members: RingBuffer
   
.. automodule:: liesl.buffers.blockbuffer
   :members: SimpleBlockBuffer

.. automodule:: liesl.files.run
   :members: Run
