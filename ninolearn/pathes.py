"""
This module contains a collection of pathes which are used within NinoLearn.

NOTE: Specifiy the datadir in a private module which you may not commit to
you public repository
"""
from os.path import join

try:
    from predictions.s0_start import datadir
except ImportError:
    raise ImportError("Cannot import name 'datadir'. Specifiy the path to your data directory using the name 'datadir' in the  ninolearn.private module which you may not commit to you public repository")

try:
    from predictions.s0_start import basedir
except ImportError:
    raise ImportError("Cannot import name 'basedir'. Specifiy the path to the root directory of ninolearn")

rawdir = join(datadir, 'raw')
processeddir = join(datadir, 'processed')
modeldir = join(datadir, 'model')
infodir = join(datadir, 'info')
preddir = join(datadir, 'predictions')