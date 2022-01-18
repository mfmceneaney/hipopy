#----------------------------------------------------------------------#
# Example script for writing HIPO files
# Authors: M. McEneaney (2022, Duke University)
#----------------------------------------------------------------------#

import numpy as np
import numpy.ma as ma
import awkward as ak
import hipopy.hipopy as hippy

# TODO: Relocate this to some other functions for iterating input files like uproot
if __name__=="__main__":

    # Writing to a new file #NOTE: Appending to files coming soon.
    print("#----------------------------------------------------------------------#")
    filename = "out.hipo" # Creates this in your $PWD
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
