#----------------------------------------------------------------------#
# Example script for reading HIPO files
# Authors: M. McEneaney (2022, Duke University)
#----------------------------------------------------------------------#

import numpy as np
import numpy.ma as ma
import awkward as ak
import hippy

# TODO: Relocate this to some other functions for iterating input files like uproot
if __name__=="__main__":

    # Reading a single file
    print("#----------------------------------------------------------------------#")
    bankName = "NEW::bank"
    item = "px"
    maxEvents = 3
    filename = '../misc/test.hipo'
    counter = 0

    file = hippy.open(filename,mode="r")
    file.show()
    file.showBank(bankName)
    file.readBank(bankName) #IMPORTANT! Call readBank BEFORE you loop through the file.
    
    # Loop through events in file
    for event in file:
        data = file.getDoubles(bank,item)
        print("counter = ",counter)
        print("data = ",data)
        counter += 1
        if counter == maxEvents: break

    # Reading a chain of files
    print("#----------------------------------------------------------------------#")
    filenames = ['../misc/test.hipo','../misc/out.hipo']
    banks = ["NEW::bank"]
    counter = 0
    step = 100

    # Loop through batches of step # events in the chain.
    for batch in hippy.iterate(filenames,banks,step=step):
        print(batch.keys())
        print(len(batch["NEW::bank_px"]))
        if counter == 0: print(ak.Array(batch["NEW::bank_px"]))
        counter += 1
        if counter % step == 0: print("counter = ",counter)

    # Writing to a new file
    print("#----------------------------------------------------------------------#")
    filename = "out.hipo"
    bank     = "NEW::bank"
    dtype    = "D" #NOTE: For now all the bank entries have to have the same type.
    names    = ["px","py","pz"]
    namesAndTypes = {e:dtype for e in names}
    rows = 7 # Chooose a #
    nEvents = 10 # Choose a #
    step = 5 # Choose a #

    file = hippy.create(filename)
    file.newTree(bank,namesAndTypes)
    file.open(mode="w") # IMPORTANT!  Open AFTER calling newTree, otherwise the banks will not be written!

    # Write events to file
    for _ in range(nEvents):
        data = np.random.random(size=(step,len(names),rows))
        file.extend({
            bank : data
        })

    file.close() #IMPORTANT! ( Can also use file.write() )
