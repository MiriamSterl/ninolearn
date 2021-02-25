"""
STEP 2: PREPROCESS DATA
The downloaded data needs to be prepared to have the similar time-axis.
In addition, the wind stress field is computed, and the latest common date of 
the observations is determined.
"""

import numpy as np
import pandas as pd
import xarray as xr
from os.path import join
from ninolearn.utils import print_header
from ninolearn.preprocess.prepare import prep_oni, prep_wwv, prep_dmi, prep_K_index, prep_wwv_proxy
from ninolearn.pathes import processeddir
import datetime
from s0_start import current_year, current_month, start_pred_y, start_pred_m

# TODO: can perhaps be merged with download.
print_header("Prepare Data")

# =============================================================================
# Prepare the indices
# =============================================================================
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
# TODO: find folder to put in
print_header("Saving enddate of observations")
f = open("enddate.txt", "x")
f.write(endyr)
f.write("\n")
f.write(endmth)
f.close()
