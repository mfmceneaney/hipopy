Examples
========

.. _examples:

Opening a HIPO File
----------------

To open a single HIPO file use the
``hipopy.hipopy.open(filename,mode='r')`` function:

.. autofunction:: hipopy.hipopy.open

The ``mode`` parameter should be either ``"r"``, ``"w"``,
or ``"a"`` (read, write, and append).

For example:

>>> import hipopy.hipopy
>>> f = hipopy.hipopy.open('file.hipo',mode='r')
>>> f.show()
               NEW::bank :     1     1     3
>>> f.read('NEW::bank')

Reading a Single File
---------------------
Coming soon!

Iterating Many Files
--------------------

To loop through many files use the 
``hipopy.hipopy.iterate(filenames,banks=None,step=100)`` function.
Batch columns are named using the bank name + item name joined by an underscore.

For example:

>>> import hipopy.hipopy
>>> for batch in hipopy.hipopy.iterate(['*.hipo'],banks=["NEW::bank"],step=10):
>>>     print(batch.keys())
>>>     break
>>> ['NEW::bank_px','NEW::bank_py','NEW::bank_pz']

Writing Files
-------------
Coming soon!

Extending Files
---------------
Coming soon!
