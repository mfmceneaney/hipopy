Examples
========

.. _examples:

Opening a HIPO File
----------------

To open a single HIPO file use the
``hipopy.hipopy.open`` function:

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
After opening a file in read mode you can check available 
names or names and types with the functions 
``hipofile.getNames`` and ``hipofile.getNamesAndTypes``.
If you know the column names and types you want
simply loop through events using the `hipofile` get methods
to access the data.

>>> import hipopy.hipopy
>>> file = hipopy.hipopy.open('file.hipo',mode='r')
>>> file.show()
               NEW::bank :     1     1     3
>>> file.readBank('NEW::bank')
>>> file.showBank('NEW::bank')
{NEW::bank/1/1}{px/D,py/D,pz/D}
>>> file.getNamesAndTypes('NEW::bank')
{'px': 'D', 'py': 'D', 'pz': 'D'}
>>> for event in file:
>>>        data = file.getDoubles('NEW::bank','px')
>>>        print(event)

Iterating Many Files
--------------------
To loop through many files use the 
``hipopy.hipopy.iterate`` function.
Batch columns are named using the bank name + item name joined by an underscore.

For example:

>>> import hipopy.hipopy
>>> for batch in hipopy.hipopy.iterate(['*.hipo'],banks=["NEW::bank"],step=10):
>>>     print(batch.keys())
>>>     break
>>> ['NEW::bank_px','NEW::bank_py','NEW::bank_pz']

Writing Files
-------------
To write a new hipofile use the ``hipopy.hipopy.create`` function.

.. note::
   This will overwrite the file if it already exists!

>>> import numpy as np
>>> import hipopy.hipopy as hipopy
>>>
>>> filename = 'new.hipo'
>>> bank     = "NEW::bank"
>>> dtype    = "D" #NOTE: For now all the bank entries have to have the same type.
>>> names    = ["px","py","pz"]
>>> namesAndTypes = {e:dtype for e in names}
>>> rows = 7 # Chooose a #
>>> nbatches = 10 # Choose a #
>>> step = 5 # Choose a # (events per batch)
>>>
>>> # Open file
>>> file = hipopy.create(filename)
>>> file.newTree(bank,namesAndTypes)
>>> file.open() # IMPORTANT:  Open AFTER calling newTree, otherwise the banks will not be written!
>>>
>>> # Write batches of events to file
>>> for _ in range(nbatches):
>>>     data = np.random.random(size=(step,len(names),rows))
>>>     file.extend({
>>>         bank : data
>>>     })
>>>
>>> file.close() # Can also use file.write()

Extending Files
---------------
To append banks to events in an existing file you must specify the type

>>> filename = "out.hipo" # Recreate this in your $PWD
>>> bank     = "NEW::bank2"
>>> dtype    = "D" #NOTE: For now all the bank entries have to have the same type.
>>> names    = ["energy","mass"]
>>> namesAndTypes = {e:dtype for e in names}
>>> rows = 7 # Chooose a #
>>> nbatches = 10 # Choose a #
>>> step = 5 # Choose a #
>>> 
>>> file = hippy.recreate(filename)
>>> file.newTree(bank,namesAndTypes)
>>> file.open() # IMPORTANT!  Open AFTER calling newTree, otherwise the banks will not be written!
>>> 
>>> # Write events to file
>>> for _ in range(nbatches):
>>>    data = np.random.random(size=(step,len(names),rows))
>>>    file.extend({
>>>       bank : data
>>>    })
>>> 
>>> file.close() #IMPORTANT! ( Can also use file.write() )

If you instead want to read the events one by one and append additional banks
to each event you can use the ``hipofile.update()`` function.  Make sure to 
**explicitly** add events to which you do not append data, otherwise they will
not be written.

>>> # Open file
>>> filename = "test.hipo" # Recreate this in your $PWD
>>> bank     = "NEW::bank2"
>>> dtype    = "D" #NOTE: For now all the bank entries have to have the same type.
>>> names    = ["energy","mass"]
>>> namesAndTypes = {e:dtype for e in names}
>>> rows = 7 # Chooose a #
>>> nbatches = 10 # Choose a #
>>> step = 1 # Choose a #
>>> 
>>> file = hippy.recreate(filename)
>>> file.newTree(bank,namesAndTypes)
>>> file.open() # IMPORTANT!  Open AFTER calling newTree, otherwise the banks will not be written!
>>> 
>>> counter = 0
>>> 
>>> for event in file:
>>>     counter += 1
>>>     data = np.random.random(size=(len(names),rows))
>>>     
>>>     # Add data to even events
>>>     if counter % 2 == 0: file.update({bank : data})
>>>     else: file.update({}) #NOTE: Important to write empty events too!
>>> 
>>> file.close() #IMPORTANT!
