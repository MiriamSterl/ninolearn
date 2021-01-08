"""
The downloaded data needed to be prepared to have the similar time-axis.

All spatial data is regridded to the 2.5x2.5 grid of the NCEP
reanalysis data.

Some variables are computed, i.e the wind stress field, the wind speed and
the warm pool edge.
"""
import numpy as np
from ninolearn.utils import print_header
from ninolearn.preprocess.prepare import prep_oni, prep_wwv, prep_iod, prep_K_index, prep_wwv_proxy

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
# Calculate some variables
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
