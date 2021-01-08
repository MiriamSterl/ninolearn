"""
The following script downloads all data that is used to train the models.
"""
from start import basedir
import sys  
sys.path.append(basedir)


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
