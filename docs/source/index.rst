.. inpost-python documentation master file, created by
   sphinx-quickstart on Sun Jan 15 18:32:27 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to inpost-python's documentation!
=========================================

.. note::

   This project is under active development.

.. code-block:: python

   from inpost.api import Inpost

   inp = await Inpost.from_phone_number('555333444')
   await inp.send_sms_code():
   ...
   if await inp.confirm_sms_code(123321):
      print('Congratulations, you initialized successfully!')



.. toctree::

   usage

.. toctree::

   api

   parcels

   exceptions


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
