.. siginfo documentation master file, created by
   sphinx-quickstart on Mon Feb 18 06:38:10 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

siginfo!
===================================

Easy debugging
--------------

Easy process monitoring
-----------------------

``siginfo`` is a Python library for easy debugging and process monitoring.

Simply import the library, initiate a ```Siginfo``` class and run your regular script. You can get progress updates by sending ``SIGNINFO`` to your Python process. 


Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

SiginfoBasic
====================
.. autoclass:: siginfo.siginfoclass.SiginfoBasic
   :members:
   :no-private-members:
   :no-special-members:

SigInfoPDB
====================
.. autoclass:: siginfo.siginfoclass.SigInfoPDB
   :members:
   :inherited-members:
   :show-inheritance:


SigInfoSingle
=====================
.. autoclass:: siginfo.siginfoclass.SigInfoSingle
   :members:
   :inherited-members:
   :show-inheritance:

locals
===================
.. automodule:: siginfo.localclass
   :members:

utils
===================
.. automodule:: siginfo.utils
   :members:
