=========
pyUAVLink
=========



.. image:: https://img.shields.io/pypi/v/pyuavlink.svg
   :target: https://pypi.org/project/pyuavlink/
   :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/l/pyuavlink.svg
   :target: https://pypi.org/project/pyuavlink/
   :alt: License

.. image:: https://img.shields.io/pypi/pyversions/pyuavlink.svg
   :target: https://pypi.org/project/pyuavlink/
   :alt: Supported Python versions




**pyUAVLink** is a Python binding and simulation controller for UAV networking protocols, built on top of ns-3 via a custom shared memory interface.

It enables real-time UAV-to-UAV (U2U) communication simulations with machine learning integration. This package acts as a bridge between Python and C++ (ns-3), making it possible to apply neural networks (e.g., LSTM) to network behavior prediction.



Features
--------

- Simulation control via `UAVLinkSimulation`
- Shared memory communication with a customized ns-3-dev module
- Real-time MCS prediction integration via LSTM