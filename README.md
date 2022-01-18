# HIPPy: an UpROOT-like I/O Interface for CLAS12 HIPO Files

## Installation

To install from source:
```bash
git --recurse-submodules clone https://github.com/mfmceneaney/hippy.git
cd hippy
cd hipo; cd lz4; make CFLAGS=-fPIC; cd ..; make; cd ..
```

To install with pip:
```bash
pip install hippy
```

## Getting Started

Check out the example scripts in `tutorials`.  More functionality coming soon!

#

Contact: matthew.mceneaney@duke.edu