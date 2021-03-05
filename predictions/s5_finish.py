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

import shutil
from os.path import exists
from ninolearn.pathes import rawdir, processeddir, modeldir, infodir


def remove_dir(dir_name):
    if exists(dir_name):
        shutil.rmtree(dir_name)
        print('%s removed' % dir_name)
    else:
        print('%s is already removed' % dir_name)

remove_dir(rawdir)
remove_dir(processeddir)
remove_dir(modeldir)
remove_dir(infodir)

print("\nDone!")