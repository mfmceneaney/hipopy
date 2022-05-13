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

    
    # Simultaneously reading and appending banks to existing file
    print("#----------------------------------------------------------------------#")
    # Open file
    filename = "out.hipo" # Recreate this in your $PWD
    bank     = "NEW::bank3"
    dtype    = "D" #NOTE: For now all the bank entries have to have the same type.
    names    = ["vx","vy","vz"]
    namesAndTypes = {e:dtype for e in names}
    rows = 7 # Chooose a #
    nbatches = 10 # Choose a #
    step = 5 # Choose a #

    file = hippy.recreate(filename)
    file.newTree(bank,namesAndTypes)
    file.open() # IMPORTANT!  Open AFTER calling newTree, otherwise the banks will not be written!

    counter = 0

    # Read file event by event
    for event in file:
        counter += 1
        print(event)
        data = np.random.random(size=(len(names),rows))
        
        # Add data to even events
        if counter % 2 == 0: file.update({bank : data})
        else: file.update({}) #NOTE: Important add odd events too!

    file.close() #IMPORTANT! ( Can also use file.write() )
