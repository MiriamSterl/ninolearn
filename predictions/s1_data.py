"""
STEP 1: DOWNLOADING AND PREPARING DATA
All data that is used to train the models is downloaded.
The downloaded data needs to be prepared to have the similar time-axis.
In addition, the wind stress field is computed, and the latest common date of 
the observations is determined.
"""

from s0_start import basedir
import sys  
sys.path.append(basedir)
#%%
# =============================================================================
# Create relevant data directories
# =============================================================================

from ninolearn.pathes import rawdir, processeddir, modeldir, infodir, basedir
from os.path import join, exists
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
    
if not exists(infodir):
    print("Make a data directory at %s" % infodir)
    mkdir(infodir)


# =============================================================================
# Download data sets
# =============================================================================

from ninolearn.download import download, sources
from ninolearn.utils import print_header

print_header("Download Data")

download(sources.ONI)
download(sources.DMI)
download(sources.WWV)
download(sources.KINDEX)
download(sources.UWIND_NCEP)
download(sources.VWIND_NCEP)



# =============================================================================
# Prepare the indices
# =============================================================================
from ninolearn.preprocess.prepare import prep_oni, prep_wwv, prep_dmi, prep_K_index, prep_wwv_proxy
from ninolearn.pathes import processeddir, infodir

print_header("Prepare Data")

prep_oni()
prep_wwv()
prep_dmi()
prep_K_index()
prep_wwv_proxy()


# =============================================================================
# Prepare the gridded data
# =============================================================================
from ninolearn.IO import read_raw
from ninolearn.preprocess.anomaly import postprocess

uwind = read_raw.uwind()
postprocess(uwind)

vwind = read_raw.vwind()
postprocess(vwind)


# =============================================================================
# Calculate wind speed and wind stress in x-direction
# =============================================================================
import numpy as np

wspd = np.sqrt(uwind**2 + vwind**2)
wspd.attrs = uwind.attrs.copy()
wspd.name = 'wspd'
wspd.attrs['long_name'] = 'Monthly Mean Wind Speed at sigma level 0.995'
wspd.attrs['var_desc'] = 'wind-speed'
postprocess(wspd)

taux = uwind * wspd
taux.attrs = uwind.attrs.copy()
taux.name = 'taux'
taux.attrs['long_name'] = 'Monthly Mean Zonal Wind Stress at sigma level 0.995'
taux.attrs['var_desc'] = 'x-wind-stress'
taux.attrs['units'] = 'm^2/s^2'
postprocess(taux)


# =============================================================================
# Determine earliest enddate that is in all datasets to be used for training
# =============================================================================
import pandas as pd
import xarray as xr
import datetime
from s0_start import current_year, current_month, start_pred_y, start_pred_m


oni = pd.read_csv(join(processeddir,'oni.csv'),index_col=0, parse_dates=True)
wwv = pd.read_csv(join(processeddir,'wwv_proxy.csv'),index_col=0, parse_dates=True)
dmi = pd.read_csv(join(processeddir,'dmi.csv'),index_col=0, parse_dates=True)
taux = xr.open_dataarray(join(processeddir,'taux_NCEP_anom.nc'))

# Enddates of processed data sets
oni_end = oni.index[-1]
wwv_end = wwv.index[-1]
dmi_end = dmi.index[-1]
taux_end = pd.Timestamp(taux.time.values[-1])

# Find latest common date of observations
latest = min(oni_end,wwv_end,dmi_end,taux_end)
 
# Check if end of observations is before start of predictions.
# If not, take current month+year as enddate.
# TODO: denk na of deze malle check wel nodig is. (nu je de huidige maand invult)
if latest < datetime.datetime(start_pred_y, start_pred_m,1,0,0): 
    endyr = str(latest.year)
    endmth = str(latest.month)
else:
    endyr = str(current_year)
    endmth = str(current_month)

# Save enddate of observations to be used
print_header("Saving enddate of observations")
f = open(join(infodir,"enddate.txt"), "x")
f.write(endyr)
f.write("\n")
f.write(endmth)
f.close()

