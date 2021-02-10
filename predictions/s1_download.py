"""
STEP 1: DOWNLOAD
All data that is used to train the models is downloaded.
"""

from s0_start import basedir
import sys  
sys.path.append(basedir)
#%%
# =============================================================================
# Checking year and month from start.py
# =============================================================================
from s0_start import start_pred_y, start_pred_m

if not isinstance(start_pred_y,int):
    raise TypeError('start_pred_y must be int')
    
if not isinstance(start_pred_m,int):
    raise TypeError('start_pred_m must be int')
    
if start_pred_m<1 or start_pred_m>12:
    raise ValueError('start_pred_m must be a number between 1 and 12')

# =============================================================================
# Create relevant data directories
# =============================================================================

from ninolearn.pathes import rawdir, processeddir, modeldir, basedir
# TODO: perhaps sth like 'infodir' for lead times, predictions etc?
from os.path import exists
from os import mkdir

if not exists(rawdir):
    print("Make a data directory at %s" % rawdir)
    mkdir(rawdir)
    
if not exists(processeddir):
    print("Make a data directory at %s" % processeddir)
    mkdir(processeddir)
    
if not exists(modeldir):
    print("Make a data directory at %s" % modeldir)
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
