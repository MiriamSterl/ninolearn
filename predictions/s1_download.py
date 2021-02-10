"""
All data that is used to train the models is downloaded.
"""

from s0_start import basedir
import sys  
sys.path.append(basedir)

# =============================================================================
# Checking year and month from start.py
# =============================================================================
# from s0_start import year, month

# if not isinstance(year,int):
#     raise TypeError('year must be int')
    
# if not isinstance(month,int):
#     raise TypeError('month must be int')
    
# if month<1 or month>12:
#     raise ValueError('month must be a number between 1 and 12')

# =============================================================================
# Create relevant data directories
# =============================================================================

from ninolearn.pathes import rawdir, processeddir, modeldir, basedir
from os.path import exists
from os import mkdir

if not exists(rawdir):
    print("make a data directory at %s" % rawdir)
    mkdir(rawdir)
    
if not exists(processeddir):
    print("make a data directory at %s" % processeddir)
    mkdir(processeddir)
    
if not exists(modeldir):
    print("make a data directory at %s" % modeldir)
    mkdir(modeldir)


# =============================================================================
# Download data sets
# =============================================================================

from ninolearn.download import download, sources
from ninolearn.utils import print_header

print_header("Download Data")

download(sources.ONI)
download(sources.IOD)
download(sources.WWV)
download(sources.KINDEX)
download(sources.UWIND_NCEP)
download(sources.VWIND_NCEP)
