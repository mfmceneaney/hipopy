# HIPOPy: UpROOT-like I/O Interface for CLAS12 HIPO Files

## Installation

To install from source:
```bash
git --recurse-submodules clone https://github.com/mfmceneaney/hipopy.git
cd hipopy
cd hipo; cd lz4; make CFLAGS=-fPIC; cd ..; cmake .; make; cd ..
```
Then add to following to your startup script:
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/hipopy
```

To install with pip:
```bash
pip install hipopy
```

## Getting Started

Check out the example scripts in `tutorials`.  More functionality coming soon!

#

Contact: matthew.mceneaney@duke.edu
