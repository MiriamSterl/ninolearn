"""
The following script downloads all data that is used to train the models.
"""
#from start import filedir
#import sys  
#sys.path.append(filedir)

from ninolearn.download import download, sources
from ninolearn.utils import print_header

print_header("Download Data")

# =============================================================================
# Single files
# =============================================================================
download(sources.SST_ERSSTv5)
download(sources.ONI)
download(sources.IOD)
download(sources.WWV)
download(sources.KINDEX)
download(sources.UWIND_NCEP)
download(sources.VWIND_NCEP)

# =============================================================================
# Multiple files
# =============================================================================
for i in range(1958, 2018): 
    sources.ORAS4['filename'] = f'zos_oras4_1m_{i}_grid_1x1.nc'
    download(sources.ORAS4, outdir = 'ssh_oras4')
