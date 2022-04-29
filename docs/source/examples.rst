Examples
========

.. _examples:

Opening a HIPO file
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

Iterating Many Files
--------------------

To loop through many files use the 
``hipopy.hipopy.iterate(filenames,banks=None,step=100)`` function.
Batch columns are named using the bank name + item name joined by an underscore.

For example:
>>> import numpy
>>> import hipopy.hipopy
>>> px = []
>>> for batch in hipopy.hipopy.iterate(['*.hipo'],banks=["NEW::bank"],step=10):
...     print(batch)
...     break
>>> {'NEW::bank_px': [array([0.64771266, 0.92349392, 0.68888959, 0.96282997, 0.59879908, 0.03549743, 0.20872965])],
     'NEW::bank_py': [array([0.35653561, 0.85208749, 0.10459373, 0.87640167, 0.97091085, 0.77093875, 0.16752778])],
     'NEW::bank_pz': [array([0.14479276, 0.46332196, 0.88259718, 0.67739049, 0.16631716, 0.551377  , 0.0996518 ])]}

Writing / Appending Files
-------------------------
Coming soon!
