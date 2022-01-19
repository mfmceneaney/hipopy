#----------------------------------------------------------------------#
# Example script for reading HIPO files
# Authors: M. McEneaney (2022, Duke University)
#----------------------------------------------------------------------#

import numpy as np
import numpy.ma as ma
import awkward as ak
import hipopy.hipopy as hippy

# TODO: Relocate this to some other functions for iterating input files like uproot
if __name__=="__main__":

    # Reading a single file
    print("#----------------------------------------------------------------------#")
    bankName = "NEW::bank"
    item = "px"
    maxEvents = 3
    filename = 'misc/test.hipo'
    counter = 0

    file = hippy.open(filename,mode="r")
    file.show()
    file.showBank(bankName)
    file.readBank(bankName) #IMPORTANT! Call readBank BEFORE you loop through the file.
    
    # Loop through events in file
    for event in file:
        data = file.getDoubles(bankName,item)
        print("counter = ",counter)
        print("data = ",np.array(data))
        counter += 1
        if counter == maxEvents: break

    # Reading a chain of files
    print("#----------------------------------------------------------------------#")
    filenames = ['misc/tes*.hipo','misc/out.hipo'] #NOTE: Make sure to specify the full path or relative path from directory in which you call this script.
    banks = ["NEW::bank"]
    counter = 0
    step = 100

    # Loop through batches of step # events in the chain.
    for batch in hippy.iterate(filenames,banks,step=step): # If you don't specify banks, ALL banks will be read.
        print(batch.keys())
        print(len(batch["NEW::bank_px"]))
        if counter == 0: print(ak.Array(batch["NEW::bank_px"]))
        counter += 1
        if counter % step == 0: print("counter = ",counter)
