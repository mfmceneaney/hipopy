#----------------------------------------------------------------------#
# Example script for writing HIPO files
# Authors: M. McEneaney (2022, Duke University)
#----------------------------------------------------------------------#

import numpy as np
import numpy.ma as ma
import awkward as ak
import hipopy.hipopy as hippy

if __name__=="__main__":

    # Appending banks to existing file
    print("#----------------------------------------------------------------------#")
    # Open file
    filename = "out.hipo" # Recreate this in your $PWD
    bank     = "NEW::bank2"
    dtype    = "D" #NOTE: For now all the bank entries have to have the same type.
    names    = ["energy","mass"]
    namesAndTypes = {e:dtype for e in names}
    rows = 7 # Chooose a #
    nbatches = 10 # Choose a #
    step = 5 # Choose a #

    file = hippy.recreate(filename)
    file.newTree(bank,namesAndTypes)
    file.open() # IMPORTANT!  Open AFTER calling newTree, otherwise the banks will not be written!
    
    # Write events to file
    for _ in range(nbatches):
        data = np.random.random(size=(step,len(names),rows))
        file.extend({
            bank : data
        })
    
    file.close() #IMPORTANT! ( Can also use file.write() )
