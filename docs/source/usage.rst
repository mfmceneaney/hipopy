Usage
=====

.. _installation:

Installation
------------

To use Hipopy, first install it using pip:

.. code-block:: console

   (.venv) $ pip install hipopy

Reading Files
----------------

To read a single file open it with the
``hipopy.hipopy.open(filename,mode='r')`` function:

.. autofunction:: hipopy.hipopy.open

The ``mode`` parameter should be either ``"r"``, ``"w"``,
or ``"a"`` (read, write, and append). Otherwise, :py:func:`hipopy.hipopy.open`
will raise an exception.

.. autoexception:: hipopy.hipopy.HipopyError

For example:

>>> import hipopy.hipopy
>>> f = hipopy.hipopy.open('file.hipo',mode='r')
>>> f.show()
               NEW::bank :     1     1     3
>>> f.read('NEW::bank')
