"""
STEP 5: FINISH
Remove the directories and files with (raw and processed) data, trained models,
and information saved in between.
Next month you can have a fresh start!
Note: the folder with the predictions data is NOT removed.
"""
from s0_start import basedir
import sys  
sys.path.append(basedir)

import os
from ninolearn.pathes import rawdir, processeddir, modeldir, infodir

os.remove(rawdir)
os.remove(processeddir)
os.remove(modeldir)
os.remove(infodir)

print("Done!")