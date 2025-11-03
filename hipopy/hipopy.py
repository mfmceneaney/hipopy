# pylint: disable=invalid-name
# pylint: disable=too-many-lines
# pylint: disable=redefined-builtin)
# pylint: disable=no-member
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-positional-arguments

"""
This module provides classes and functions for handling HIPO files with ease.
"""

import os
import glob
import shutil
import numpy as np
import hipopybind

# ----------------------------------------------------------------------#
# Basic  I/O behaviors


def open(filename, mode="r", tags=None):
    """
    Parameters
    ----------
    filename : string, required
    mode : string, optional
        File mode ("r" : read, "w" : write, "a" : append)
        Default : "r"
    tags : int or list of ints, optional
        Set bank tags for reader to use.  0 works for most banks.
        1 is needed for scaler banks.
        Default : None

    Description
    -----------
    Open a HIPO file to read.
    """
    f = hipofile(filename, mode=mode, tags=tags)
    f.open()
    return f


def iterate(files, banks=None, step=100, tags=None, experimental=True):
    """
    Parameters
    ----------
    files : list, required
        List of file names
    banks : list, optional
        List of bank names to read
        Default : None
    step : int, optional
        Batch size for iterating through file events
        Default : 100
    tags : int or list of ints, optional
        Set bank tags for reader to use.  0 works for most banks.
        1 is needed for scaler banks.
        Default : None
    experimental : bool, optional
        Whether to use experimental hipopybind.HipoFileIterator to iterate files
        Default : True

    Description
    -----------
    Iterate through a list of hipofiles reading all banks unless
    specific banks are specified. Iteration is broken into batches
    of step events.
    """
    if tags is None and experimental:
        tags = []
    f = hipochain(files, banks, step=step, tags=tags, experimental=experimental)
    return f


def create(filename):
    """
    Parameters
    ----------
    filename : string, required

    Description
    -----------
    Open a HIPO file to write (overwrites existing files).
    """
    f = hipofile(filename, mode="w")
    return f


def recreate(filename):
    """
    Parameters
    ----------
    filename : string, required

    Description
    -----------
    Open an existing HIPO file to write more banks.  Note that this
    just opens the reader.  To open the writer, call `hipofile.open()`
    again explicitly after adding schema you want to write.
    """
    f = hipofile(filename, mode="a")
    f.open()
    return f


# ----------------------------------------------------------------------#
# Classes: hipofile, hipofileIterator, hipochain, hipochainIterator


class hipofile:
    """
    Attributes
    ----------
    filename : string
        Full path name of HIPO file
    mode : string
        File mode ("r" : read, "a" : append, "w" : write)
    reader : hipopybind.Reader
        HIPO file reader
    writer : hipopybind.Writer
        HIPO file writer
    dictionary : hipopybind.Dictionary
        HIPO file schema dictionary
    event : hipopybind.Event
        HIPO event for reading and writing banks
    group : int
        Group number for current HIPO bank (not unique)
    item : int
        Item number for current HIPO bank (unique)
    dtypes : dict
        Dictionary to datatypes
    buffext : string
        Extension for buffer file
    buffname : string
        Name of buffer file
    banklist : dict
        Dictionary to hipopybind.Bank objects
    """

    def __init__(self, filename, mode="r", tags=None):
        """
        Parameters
        ----------
        filename : string, required
            Full path name of HIPO file
        mode : string, optional
            File mode ("r" : read, "w" : write, "a" : append)
            Default : "r"
        """
        self.filename = filename
        self.reader = hipopybind.Reader() if mode != "w" else None
        self.writer = hipopybind.Writer() if mode != "r" else None
        self.dictionary = hipopybind.Dictionary()
        self.event = hipopybind.Event()
        self.mode = mode  # "r" : read, "w" : write, "a" : append
        self.group = 1
        self.item = 0
        self.dtypes = {}
        self.buffext = "~"
        self.buffname = None
        self.banklist = {}
        self.tags = tags

    def __len__(self):
        """
        Return
        ------
        Length of the file
        """
        return self.reader.getEntries()

    def open(self):
        """
        Description
        -----------
        Open a HIPO file to read, write (from scratch), or append data.
        IMPORTANT:  Make sure you add schema before opening a file to write!
        """

        if self.mode == "r":
            if self.tags is not None:
                if isinstance(self.tags, int):
                    self.reader.setTags(
                        self.tags
                    )  # NOTE: Only set tags reading since not tested for writing yet.
                else:
                    for tag in self.tags:
                        self.reader.setTags(tag)
            self.reader.open(self.filename)
            self.reader.readDictionary(self.dictionary)
        elif self.mode == "w":
            self.writer.open(self.filename)
        elif self.mode == "a" and self.buffname is None:

            # Open with reader first
            self.reader.open(self.filename)
            self.reader.readDictionary(self.dictionary)

            # Set item number to highest so far
            self.item = 0
            for schema in self.dictionary.getSchemaList():
                i = self.dictionary.getSchema(schema).getItem()
                self.item = max(self.item, i)

            # Add existing banks to writer dictionary if in append mode
            if self.mode == "a":
                self.writer.addDictionary(self.dictionary)

            # Set buffername
            self.buffname = (
                self.filename + self.buffext
            )  # NOTE: Separate code here so that you can call addSchema()

        elif self.mode == "a" and self.buffname is not None:
            # Now open with writer after adding schema to write
            self.writer.open(self.buffname)

        # Create banks now for speed
        _dictionary = (
            self.dictionary if self.mode == "r" else self.writer.getDictionary()
        )
        for schema in _dictionary.getSchemaList():
            self.banklist[schema] = hipopybind.Bank(_dictionary.getSchema(schema))
            self.event.getStructure(
                self.banklist[schema]
            )  # NOTE: Necessary before reading banks into event with addStructure.

    def flush(self):
        """
        Description
        -----------
        Write current HIPO writer buffer to file.
        """
        self.writer.flush()

    def close(self):
        """
        Parameters
        ----------
        mode : string, optional
            Default : "r"

        Description
        -----------
        Close osstream for an open file.
        """
        if self.mode == "r":
            pass  # NOTE: Nothing to do here.
        if self.mode == "w":
            self.writer.close()
        if self.mode == "a":
            self.writer.close()
            shutil.copy(self.buffname, self.filename)
            os.remove(self.buffname)

    def goToEvent(self, event):
        """
        Parameters
        ----------
        event : int, required
            Integer number indicating event number in file (starts at 0)

        Returns
        -------
        boolean
            True if requested event exists, otherwise False

        Description
        -----------
        Move to requested HIPO event in a file in read mode.
        """
        status = self.reader.gotoEvent(event)
        self.reader.read(self.event)
        return status

    def nextEvent(self):
        """
        Returns
        -------
        boolean
            True if next event exists else False

        Description
        -----------
        Move to next HIPO event from a file in read mode.
        """
        status = self.reader.next()
        self.reader.read(self.event)
        return status

    def addSchema(self, name, namesAndTypes, group=1, item=-1):
        """
        Parameters
        ----------
        name : string, required
            Bank name
        namesAndTypes : dictionary, required
            Map of column names to types ("D" : double, "F" : float,
            "I" : int, "B" : byte, "S" : short, "L" : long)
        group : int, optional
            Group number for bank (not unique)
            Default : 1
        item : int, optional
            Item number for bank (unique)
            Default : -1

        Description
        -----------
        Add a schema structure to HIPO file writer dictionary for
        a bank you wish to write.  NOTE: Do this BEFORE opening the
        file in write mode.
        """

        schemaString = ",".join(
            ["/".join([key, namesAndTypes[key]]) for key in namesAndTypes]
        )
        if item <= self.item or item < 0:
            self.item += 1

        schema = hipopybind.Schema(
            name, group, max(self.item, item)
        )  # NOTE: Important to use this constructor here.
        schema.parse(schemaString)
        d = hipopybind.Dictionary()
        d.addSchema(schema)
        self.writer.addDictionary(d)

    def addEvent(self):
        """
        Description
        -----------
        Adds current hipo event to buffer and advances writer to next event.
        """
        self.writer.addEvent(self.event)

    def writeEvent(self):
        """
        Description
        -----------
        Writes current hipo event buffer to file.
        """
        self.writer.flush()

    def writeAllBanks(self):
        """
        Description
        -----------
        Write all existing banks to event for appending to file.
        """
        for schema in self.writer.getDictionary().getSchemaList():
            bank = self.banklist[schema]
            self.event.addStructure(bank)

    def writeBank(self, name, names, data, dtypes="D"):
        """
        Parameters
        ----------
        name : string, required
            Bank name
        names : list, required
            Column names
        data  : numpy.ndarray, required
            2D NumPy array of dimension (columns,rows)
        dtype : string, optional
            Data type ("D" : double, "F" : float, "I" : int, "B" : byte, "S" : short, "L" : long)
            Default : "D"

        Description
        -----------
        Fill an event bank with data and write to buffer.
        """
        rows = np.shape(data)[-1]
        bank = self.banklist[name]
        bank.reset()
        bank.setRows(rows)

        # Add data to bank
        for idx, entry in enumerate(names):
            dtype = dtypes if len(dtypes) == 1 else dtypes[idx]
            if dtype == "D":
                hipopybind.putDoubles(bank, entry, data[idx].astype(float))
            elif dtype == "I":
                hipopybind.putInts(bank, entry, data[idx].astype(int))
            elif dtype == "F":
                hipopybind.putFloats(bank, entry, data[idx].astype(float))
            elif dtype == "B":
                hipopybind.putBytes(bank, entry, data[idx].astype(int))
            elif dtype == "S":
                hipopybind.putShorts(bank, entry, data[idx].astype(int))
            elif dtype == "L":
                hipopybind.putLongs(bank, entry, data[idx].astype(int))
            else:
                raise TypeError

        # Add bank to event
        self.event.addStructure(bank)

    def newTree(self, bank, bankdict, group=None, item=None):
        """
        Parameters
        ----------
        bank : string, required
            Bank name
        bankdict : dictionary, required
            Dictionary of bank entry names to data types
            ("D":double, "F":float, "I":int, "B":byte, "S":short, "L":long)
        group : int, optional
            Group identifier for bank (does not have to be unique)
            Default : None
        item : int, optional
            Item identifier for bank (must be unique)
            Default : None

        Description
        -----------
        Create a new bank to which to add data.  Mimics uproot newtree function.
        """
        group = self.group if group is None else group
        item = self.item if item is None else item
        self.addSchema(bank, bankdict, group, item)
        self.dtypes[bank] = bankdict

    def extend(self, datadict):
        """
        Parameters
        ----------
        datadict : dictionary, required
            Dictionary of bank names to data arrays of shape (nEvents,nEntries,nRows)

        Description
        -----------
        Add batched data to banks in a file.  Mimics uproot extend function.
        """
        keys = list(datadict.keys())
        nEvents = len(datadict[keys[0]])

        # Write mode routine
        if self.mode == "w":
            for event in range(nEvents):
                for (
                    bank
                ) in (
                    datadict
                ):  # This requires datadict shape to be (nEvents,nNames,nRows)
                    self.writeBank(
                        bank,
                        list(self.dtypes[bank].keys()),
                        datadict[bank][event],
                        dtypes=list(self.dtypes[bank].values()),
                    )
                self.writer.addEvent(self.event)
                self.event.reset()

        # Append mode routine
        elif self.mode == "a":
            for event in range(nEvents):
                if not self.nextEvent():
                    print(
                        " *** ERROR *** Tried to append more events"
                        + "than are in current file. Stopping."
                    )
                    break
                for (
                    bank
                ) in (
                    datadict
                ):  # This requires datadict shape to be (nEvents,nNames,nRows)
                    self.writeBank(
                        bank,
                        self.dtypes[bank].keys(),
                        datadict[bank][event],
                        dtypes=list(self.dtypes[bank].values()),
                    )
                self.writer.addEvent(self.event)
                self.event.reset()

    def update(self, datadict):
        """
        Parameters
        ----------
        datadict : dictionary, required
            Dictionary of bank names to data arrays of shape (nEntries,nRows)

        Description
        -----------
        Append one set of event banks at a time and do not progress to the
        next event automatically.
        """
        # Append mode routine
        if self.mode == "a":
            for bank in datadict:  # This requires datadict shape to be (nNames,nRows)
                self.writeBank(
                    bank,
                    self.dtypes[bank].keys(),
                    datadict[bank],
                    dtypes=list(self.dtypes[bank].values()),
                )
            self.writer.addEvent(self.event)
            self.event.reset()

    def write(self):
        """
        Description
        -----------
        Alias for self.close()
        """
        self.close()

    def hasBank(self, bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Description
        -----------
        Check if bank exists for current file.
        """
        return self.dictionary.hasSchema(bankName)

    def show(self):
        """
        Description
        -----------
        Print out all available bank names in open file.
        """
        print(self.dictionary)

    def showBank(self, bankName):
        """
        Parameters
        ---------
        bankName : string, required

        Description
        -----------
        Print out bank contents for current event.
        """
        print(self.dictionary.getSchema(bankName))

    def getBanks(self):
        """
        Returns
        -------
        list
            list of all bank names in the reader dictionary
        """
        return self.dictionary.getSchemaList()

    def readAllBanks(self):
        """
        Description
        -----------
        Read all existing banks to event for appending to file.
        """
        for schema in self.dictionary.getSchemaList():
            bank = hipopybind.Bank(self.dictionary.getSchema(schema))
            self.event.getStructure(bank)

    def readBank(self, bankName):
        """
        Parameters
        ----------
        bankName : string, required
        verbose : boolean, optional
            Print out loading message for each event if True

        Description
        -----------
        Setup to read bank contents for each event into memory.
        """
        if self.dictionary.hasSchema(bankName):
            bank = hipopybind.Bank(self.dictionary.getSchema(bankName))
            self.event.getStructure(bank)

    def getItem(self):
        """
        Description
        -----------
        Get highest number item of all existing schema in reader for initiating file in append mode.
        """
        # Set item number to highest so far
        item = 0
        for schema in self.dictionary.getSchemaList():
            i = self.dictionary.getSchema(schema).getItem()
            item = max(item, i)
        self.item = item
        return self.item

    def getEntries(self, bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Description
        -----------
        Get number of entries in bank.  Make sure you read bank first
        with readBank(bankName) method above.
        """
        return self.dictionary.getSchema(bankName).getEntries()

    def getNamesAndTypes(self, bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Returns
        -------
        data : dict
            Dictionary of bank entry names to types (represented as strings)

        Description
        -----------
        Get a list of the entry names from the data table in the current event's bank.
        """
        bankdict = None
        try:
            bankdict = self.dictionary.getSchema(bankName).getSchemaString()
            bankdict = bankdict.split("}{")[1][:-1]
            bankdict = {
                entry.split("/")[0]: entry.split("/")[1]
                for entry in bankdict.split(",")
            }
        except IndexError:
            print("hipopy.hipopy.hipofile.getNamesAndTypes schemaString unreadable")
            print("bankName = ", bankName)
            print(
                "schemaString = ", self.dictionary.getSchema(bankName).getSchemaString()
            )
            return None
        return bankdict

    def getNames(self, bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Returns
        -------
        data : list
            List of entry names in bank

        Description
        -----------
        Get a list of the entry names from the data table in the current event's bank.
        """
        schema = self.dictionary.getSchema(bankName)
        nEntries = schema.getEntries()
        return [schema.getEntryName(i) for i in range(nEntries)]

    def getTypes(self, bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Returns
        -------
        data : list
            List of entry types (represented as strings) in bank

        Description
        -----------
        Get a list of the entry types from the data table in the current event's bank.
        """
        dtypes = {1: "B", 2: "S", 3: "I", 4: "F", 5: "D", 8: "L"}
        schema = self.dictionary.getSchema(bankName)
        nEntries = schema.getEntries()
        return [dtypes[schema.getEntryType(i)] for i in range(nEntries)]

    def getRows(self, bankName):
        """
        Parameters
        ----------
        bankName : string, required

        Description
        -----------
        Get number of rows in bank.  Make sure you read bank first
        with readBank(bankName) method above.
        """
        bank = self.banklist[bankName]
        return bank.getRows()

    def getInts(self, bankName, item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name to read in bank

        Returns
        -------
        data : list
            List of ints from bank entry

        Description
        -----------
        Get a column of ints from the data table in the current event's bank.
        """
        bank = self.banklist[bankName]
        data = bank.getInts(item)
        return data

    def getFloats(self, bankName, item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name to read in bank

        Returns
        -------
        data : list
            List of floats from bank entry

        Description
        -----------
        Get a column of floats from the data table in the current event's bank.
        """
        bank = self.banklist[bankName]
        data = bank.getFloats(item)
        return data

    def getDoubles(self, bankName, item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name to read in bank

        Returns
        -------
        data : list
            List of doubles from bank entry

        Description
        -----------
        Get a column of doubles from the data table in the current event's bank.
        """
        bank = self.banklist[bankName]
        data = bank.getDoubles(item)
        return data

    def getShorts(self, bankName, item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name to read in bank

        Returns
        -------
        data : list
            List of shorts from bank entry

        Description
        -----------
        Get a column of shorts from the data table in the current event's bank.
        """
        bank = self.banklist[bankName]
        data = bank.getShorts(item)
        return data

    def getLongs(self, bankName, item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name to read in bank

        Returns
        -------
        data : list
            List of longs from bank entry

        Description
        -----------
        Get a column of longs from the data table in the current event's bank.
        """
        bank = self.banklist[bankName]
        data = bank.getLongs(item)
        return data

    def getBytes(self, bankName, item):
        """
        Parameters
        ----------
        bankName : string, required
        item : string, required
            Column name to read in bank

        Returns
        -------
        data : list
            List of bytes from bank entry

        Description
        -----------
        Get a column of bytes from the data table in the current event's bank.
        """
        bank = self.banklist[bankName]
        data = bank.getBytes(item)
        return data

    def __iter__(self):
        return hipofileIterator(self)


class hipofileIterator:
    """
    Description
    -----------
    Iterator class for hipopy.hipopy.hipoFile class
    """

    def __init__(self, hpfile):
        self.hpfile = hpfile
        self.idx = 0

        if self.hpfile.mode != "w":
            self.hpfile.readAllBanks()  # IMPORTANT!
            self.banks = self.hpfile.getBanks()
            self.verbose = False  # NOTE: Not really necessary.
            self.items = {}

            # Read all requested banks
            for b in self.banks:
                self.hpfile.readBank(b)
                helper = self.hpfile.getNamesAndTypes(
                    b
                )  # NOTE: This breaks down if you repeat with the file open.
                self.items[b] = helper

    def __next__(self):
        if (
            self.hpfile.nextEvent()
        ):  # NOTE: Good for reading but need a different method for appending!
            self.idx += 1
            event = {}

            # Get bank data
            for bank in self.banks:
                self.hpfile.event.getStructure(
                    self.hpfile.banklist[bank]
                )  # NOTE: NECESSARY OR YOU WILL NOT READ ANY DATA!
                for item in self.items[bank]:
                    data = []
                    item_type = self.items[bank][item]
                    if item_type == "D":
                        data = self.hpfile.getDoubles(bank, item)
                    elif item_type == "I":
                        data = self.hpfile.getInts(bank, item)
                    elif item_type == "F":
                        data = self.hpfile.getFloats(bank, item)
                    elif item_type == "L":
                        data = self.hpfile.getLongs(bank, item)
                    elif item_type == "S":
                        data = self.hpfile.getShorts(bank, item)
                    elif item_type == "B":
                        data = self.hpfile.getBytes(bank, item)

                    # Add bank data to event dictionary
                    event[bank + "_" + item] = [data]

            return event
        raise StopIteration


class hipochain:
    """
    Attributes
    ----------
    names : list
        List of file names in hipochain
    banks : list
        List of bank names to be read
    step : int
        Batch size for reading banks
    mode : string
        Currently fixed to always be in read mode ("r")
    verbose : boolean
        Currently fixed to always be False
    tags : int or list of ints
        Set bank tags for reader to use.  0 works for most banks.
        1 is needed for scaler banks.
    experimental : bool
        Do bank and event looping in C++ for added speed (see hipopybind package).

    Description
    -----------
    Chains files together so they may be read continuously.
    """

    def __init__(self, names, banks=None, step=100, tags=None, experimental=True):
        self.names = names

        # Parse regex NOTE: Must be full or relative path from $PWD.  ~/... does not work.
        if isinstance(self.names, str):
            self.names = glob.glob(names)
        else:
            newnames = []
            for fnames in self.names:
                files = glob.glob(fnames)
                if len(files) > 0:
                    for file in files:
                        newnames.append(file)
            self.names = newnames

        self.banks = banks
        self.step = step
        self.mode = "r"
        self.verbose = False
        self.tags = tags
        self.experimental = experimental

    def __iter__(self):
        return (
            hipochainIterator(self)
            if not self.experimental
            else hipochainIteratorExperimental(self)
        )


class hipochainIterator:
    """
    Attributes
    ----------
    chain : hipopy.hipopy.hipochain
        Hipochain object overwhich to iterate
    idx : int
        Index of current file in hipochain
    counter : int
        Event counter for batching data
    file : hipopy.hipopy.hipoFile
        Current file in hipochain
    items : dict
        Dictionary of bank names to item names to read
    dict : dict
        Dictionary into which Hipo bank data is read

    Methods
    -------
    switchFile

    Description
    -----------
    Iterator for hipopy.hipopy.hipochain class
    """

    def __init__(self, chain):
        self.chain = chain
        self.nnames = len(self.chain.names)  # NOTE: Assumes this will stay constant.
        self.idx = -1
        self.counter = 0
        self.file = None
        self.items = {}
        self.dict = None

    def switchFile(self):
        """
        Description
        -----------
        Checks if next file in chain exists and then opens and reads requested banks if so.
        """
        # Open file
        self.idx += 1  # NOTE: Do this before everything below since we initiate at -1.
        if self.idx >= self.nnames:
            return  # NOTE: Sanity check
        self.file = hipofile(
            self.chain.names[self.idx], mode=self.chain.mode, tags=self.chain.tags
        )
        self.file.open()

        if self.chain.banks is None:
            self.chain.banks = (
                self.file.getBanks()
            )  # NOTE: This assumes all the files in the chain have the same banks.

        # Read all requested banks
        for b in self.chain.banks:
            self.file.readBank(b)
            helper = self.file.getNamesAndTypes(b)
            self.items[b] = helper

    def __next__(self):
        """
        Description
        -----------
        Loops files reading requested banks if they exist
        """

        if self.idx == -1:
            self.switchFile()  # Load first file manually

        if self.idx < (self.nnames):

            # Check if output array has been initialized
            if self.dict is None:
                self.dict = {}

            # Loop events in current file
            while self.file.nextEvent():

                # Get bank data
                for bank in self.chain.banks:
                    self.file.event.getStructure(
                        self.file.banklist[bank]
                    )  # NOTE: NECESSARY OR YOU WILL NOT READ ANY DATA!
                    for item in self.items[bank]:
                        data = []
                        item_type = self.items[bank][item]
                        if item_type == "D":
                            data = self.file.getDoubles(bank, item)
                        elif item_type == "I":
                            data = self.file.getInts(bank, item)
                        elif item_type == "F":
                            data = self.file.getFloats(bank, item)
                        elif item_type == "L":
                            data = self.file.getLongs(bank, item)
                        elif item_type == "S":
                            data = self.file.getShorts(bank, item)
                        elif item_type == "B":
                            data = self.file.getBytes(bank, item)

                        # Add bank data to batch dictionary
                        if not bank + "_" + item in self.dict:
                            self.dict[bank + "_" + item] = [data]
                        else:
                            self.dict[bank + "_" + item].append(data)

                # Check size of output array
                self.counter += 1
                if self.counter % self.chain.step == 0:
                    res = self.dict
                    self.dict = None
                    return res

                # Switch the file AFTER you get through all events in file,
                # BUT remain in loop so you don't need a recursive function
                if not self.file.reader.hasNext():
                    self.switchFile()

        # Final return for remainder
        if self.dict is not None and len(self.dict.keys()) > 0:
            res = self.dict
            self.dict = None
            return res

        # Final stop
        raise StopIteration


class hipochainIteratorExperimental:
    """
    Attributes
    ----------
    chain : hipopy.hipopy.hipochain
        Hipochain object overwhich to iterate
    idx : int
        Index of current file in hipochain
    counter : int
        Event counter for batching data
    file : hipopy.hipopy.hipoFile
        Current file in hipochain
    items : dict
        Dictionary of bank names to item names to read
    dict : dict
        Dictionary into which Hipo bank data is read

    Methods
    -------
    getAllBanks

    Description
    -----------
    Experimental iterator for hipopy.hipopy.hipochain class
    """

    def __init__(self, chain):
        self.chain = chain
        self.nnames = len(self.chain.names)  # NOTE: Assumes this will stay constant.
        self.idx = -1
        self.file = None
        if self.chain.banks is None:
            self.getAllBankNames()
        self.has_events = True
        self.hbHipoFileIterator = hipopybind.HipoFileIterator(
            self.chain.names, self.chain.banks, self.chain.step, self.chain.tags
        )
        self.banknames = self.hbHipoFileIterator.banknames
        self.items = self.hbHipoFileIterator.items
        self.types = self.hbHipoFileIterator.types

    def getAllBankNames(self):
        """
        Description
        -----------
        Checks if next file in chain exists and then opens and reads requested banks if so.
        """
        # Open file
        self.idx += 1  # NOTE: Do this before everything below since we initiate at -1.
        if self.idx >= self.nnames:
            return  # NOTE: Sanity check
        self.file = hipofile(
            self.chain.names[self.idx], mode=self.chain.mode, tags=self.chain.tags
        )
        self.file.open()

        if self.chain.banks is None:
            self.chain.banks = (
                self.file.getBanks()
            )  # NOTE: This assumes all the files in the chain have the same banks.

    def __next__(self):
        """
        Description
        -----------
        Loops files reading requested banks if they exist
        """

        if self.has_events:
            self.has_events = self.hbHipoFileIterator.__next__()
            datadict = {}
            for idx, bankname in enumerate(self.banknames):
                for idx2, item in enumerate(self.items[idx]):
                    item_type = self.types[idx][idx2]
                    if item_type == 5:
                        datadict[bankname + "_" + item] = (
                            self.hbHipoFileIterator.getDoubles(bankname, item)
                        )
                    elif item_type == 4:
                        datadict[bankname + "_" + item] = (
                            self.hbHipoFileIterator.getFloats(bankname, item)
                        )
                    elif item_type == 3:
                        datadict[bankname + "_" + item] = (
                            self.hbHipoFileIterator.getInts(bankname, item)
                        )
                    elif item_type == 8:
                        datadict[bankname + "_" + item] = (
                            self.hbHipoFileIterator.getLongs(bankname, item)
                        )
                    elif item_type == 2:
                        datadict[bankname + "_" + item] = (
                            self.hbHipoFileIterator.getShorts(bankname, item)
                        )
                    elif item_type == 1:
                        datadict[bankname + "_" + item] = (
                            self.hbHipoFileIterator.getBytes(bankname, item)
                        )
            return datadict
        raise StopIteration
