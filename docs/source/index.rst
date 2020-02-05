.. LieSL documentation master file, created by
   sphinx-quickstart on Thu Dec  5 21:22:28 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to LieSL's documentation!
=================================

.. image:: https://github.com/pyreiz/pyliesl/workflows/pytest/badge.svg
  :target: https://github.com/pyreiz/pyliesl/actions

.. image:: https://readthedocs.org/projects/pyliesl/badge/?version=latest
  :target: https://pyliesl.readthedocs.io/en/latest/?badge=latest

.. image:: https://coveralls.io/repos/github/pyreiz/pyliesl/badge.svg?branch=master
  :target: https://coveralls.io/github/pyreiz/pyliesl?branch=master

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://en.wikipedia.org/wiki/MIT_License


LieSL is a set of convenient tools to manage `LSL streams <https://labstreaminglayer.readthedocs.io/>`_
and record or load `xdf files <https://github.com/sccn/xdf/wiki/Specifications>`_ wrapping  `pyxdf <https://github.com/xdf-modules/xdf-Python>`_. and `LabRecorder <https://github.com/labstreaminglayer/App-LabRecorder>`_.


Installation
------------

.. code-block:: bash

    git clone git@github.com:pyreiz/pyliesl.git
    cd pyliesl
    pip install .

Basic Usage
-----------

Liesl offers a python API and a set of command line tools

Two common use case for the API are recording a set of streams with :class:`~.Session` or subscribing 
a :class:`~.RingBuffer` to a specific LSL Outlet detected by :func:`~.open_streaminfo`.

Three common use cases for the CLI are mocking a Outlet for development and testing using 
:code:`liesl mock`, printing information about all currently visible LSL outlets using 
:code:`liesl list`, or fast peeking into the content of an xdf file with 
:code:`liesl xdf <filename> --at-most 10`.

Documentation
-------------

.. toctree::
   :maxdepth: 3

   api
   cli

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
