liesl API
----------

The main API can be accessed directly from liesl, e.g.


Stream Handling
***************

Detect and print information about available streams.

.. automodule:: liesl.streams.finder
   :members: open_stream, open_streaminfo, print_available_streams, get_streams_matching, get_streaminfos_matching

.. automodule:: liesl.streams.convert
   :members: inlet_to_dict, get_channel_map


Buffers
*******



.. automodule:: liesl.buffers.ringbuffer
   :members: RingBuffer

.. automodule:: liesl.buffers.blockbuffer
   :members: SimpleBlockBuffer

.. automodule:: liesl.buffers.response
   :members: Response, MockResponse


Recording
*********

.. automodule:: liesl.files.run
   :members: Run
   
.. automodule:: liesl.files.session
   :members: Session


