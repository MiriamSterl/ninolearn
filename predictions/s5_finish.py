"""
STEP 5: FINISH
Remove the directories and files with (raw and processed) data, trained models,
and information saved in between.
Next month you can have a fresh start!
"""
import os
from ninolearn.pathes import rawdir, processeddir, modeldir, infodir

os.remove(rawdir)
os.remove(processeddir)
os.remove(modeldir)
os.remove(infodir)