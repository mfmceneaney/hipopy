# HIPOPy: UpROOT-like I/O Interface for CLAS12 HIPO Files

## Prerequisites

* Python >=3.7.3
* A compiler with C++11 support
* Pip 10+ or CMake >= 3.4 (or 3.14+ on Windows, which was the first version to support VS 2019)
* Ninja or Pip 10+

You will also need to install the project dependencies:
* [numpy](https://numpy.org)
* [awkward](https://awkward-array.readthedocs.io/en/latest/)
* [hipopybind](https://github.com/mfmceneaney/hipopybind.git)

(All available with pip.)

## Installation

To install with pip:
```bash
pip install hipopy
```

To install from source:
```bash
git clone https://github.com/mfmceneaney/hipopy.git
```

Then add to following to your startup script:
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/hipopy
```

## Getting Started

Check out the example scripts in `tutorials`.  More functionality coming soon!

## Documentation

Full documentation available on [Read the Docs](https://hipopy.readthedocs.io/en/latest/index.html)!

#

Contact: matthew.mceneaney@duke.edu
