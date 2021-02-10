"""
The downloaded data needed to be prepared to have the similar time-axis.
In addition, the wind stress field and wind speed are computed.
"""

import numpy as np
import pandas as pd
import xarray as xr
from os.path import join
from ninolearn.utils import print_header
from ninolearn.preprocess.prepare import prep_oni, prep_wwv, prep_iod, prep_K_index, prep_wwv_proxy
from ninolearn.pathes import processeddir

print_header("Prepare Data")

# =============================================================================
# Prepare the indices
# =============================================================================
prep_oni()
prep_wwv()
prep_iod()
prep_K_index()
prep_wwv_proxy()

# =============================================================================
# Prepare the gridded data
# =============================================================================
from ninolearn.IO import read_raw
from ninolearn.preprocess.anomaly import postprocess

# NCEP reanalysis
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
iod = pd.read_csv(join(processeddir,'iod.csv'),index_col=0, parse_dates=True)
taux = xr.open_dataarray(join(processeddir,'taux_NCEP_anom.nc'))

# Enddates of processed data sets
oni_end = oni.index[-1]
wwv_end = wwv.index[-1]
iod_end = iod.index[-1]
taux_end = taux.time.values[-1]

# Find earliest enddate
earliest = oni_end
if wwv_end < earliest:
    earliest = wwv_end
if iod_end < earliest:
    earliest = iod_end
if taux_end < earliest:
    earliest = taux_end
    
endyr = str(earliest.year)
endmth = str(earliest.month)

f = open("enddate.txt", "x")
f.write(endyr)
f.write("\n")
f.write(endmth)
f.close()
