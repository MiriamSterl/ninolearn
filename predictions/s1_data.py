"""
STEP 1: DOWNLOADING AND PREPARING DATA
All data that is used to train the models is downloaded.
The downloaded data needs to be prepared to have the similar time-axis.
In addition, the wind stress field is computed, and the latest common date of 
the observations is determined.
Finally, the forecasts from IRI/CPC are downloaded and processed, so that
our forecast can later be compared to them.
"""

from s0_start import basedir
import sys  
sys.path.append(basedir)

# =============================================================================
# Create relevant data directories
# =============================================================================

from ninolearn.pathes import rawdir, processeddir, modeldir, infodir, basedir, preddir
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
    
if not exists(preddir):
    print("Make a data directory at %s" % preddir)
    mkdir(preddir)


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
download(sources.otherForecasts)



# =============================================================================
# Prepare the indices
# =============================================================================
from ninolearn.preprocess.prepare import prep_oni, prep_wwv, prep_dmi, prep_K_index, prep_wwv_proxy

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
# Prepare the IRI/CPC forecast data
# =============================================================================
from ninolearn.preprocess.prepare import prep_other_forecasts
from s0_start import start_pred_y, start_pred_m
from ninolearn.utils import num_to_month, pred_filename

# TODO: also save last_obs info in prepare.py
IRICPC = prep_other_forecasts(num_to_month(start_pred_m),str(start_pred_y))
fn = pred_filename(start_pred_y, start_pred_m)+'_iricpc.txt'
np.save(join(preddir,fn), IRICPC)


# =============================================================================
# Determine earliest enddate that is in all datasets to be used for training
# =============================================================================
import pandas as pd
import xarray as xr
import datetime

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
# If not, take last date before start of prediction as enddate.
if latest < datetime.datetime(start_pred_y, start_pred_m,1,0,0): 
    endyr = str(latest.year)
    endmth = str(latest.month)
else:
    if start_pred_m > 1:
        endyr = str(start_pred_y)
        endmth = str(start_pred_m-1)
    else:
        endyr = str(start_pred_y-1)
        endmth = str(12)

# Save enddate of observations to be used
print_header("Saving enddate of observations")
f = open(join(infodir,"enddate.txt"), "x")
f.write(endyr)
f.write("\n")
f.write(endmth)
f.close()


print("Step 1 finished, continue to step 2!")
