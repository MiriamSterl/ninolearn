"""
The following script downloads all data that is used to train the models.
"""
#from start import basedir
#import sys  
#sys.path.append(basedir)

from ninolearn.download import download, sources
from ninolearn.utils import print_header

print_header("Download Data")

download(sources.ONI)
download(sources.IOD)
download(sources.WWV)
download(sources.KINDEX)
download(sources.UWIND_NCEP)
download(sources.VWIND_NCEP)
