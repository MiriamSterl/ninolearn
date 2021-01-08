"""
The downloaded data needed to be prepared to have the similar time-axis.

All spatial data is regridded to the 2.5x2.5 grid of the NCEP
reanalysis data.

Some variables are computed, i.e the wind stress field, the wind speed and
the warm pool edge.
"""
import numpy as np
from ninolearn.utils import print_header
from ninolearn.preprocess.prepare import prep_oni, prep_wwv
from ninolearn.preprocess.prepare import prep_iod, prep_K_index, prep_wwv_proxy

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
from ninolearn.preprocess.regrid import to2_5x2_5

# postprocess sst data from ERSSTv5
sst_ERSSTv5 = read_raw.sst_ERSSTv5()
sst_ERSSTv5_regrid = to2_5x2_5(sst_ERSSTv5)
postprocess(sst_ERSSTv5_regrid)

# NCEP reanalysis
uwind = read_raw.uwind()
postprocess(uwind)

vwind = read_raw.vwind()
postprocess(vwind)

# post process values from ORAS4 ssh
ssh_oras4 = read_raw.oras4()
ssh_oras4_regrid = to2_5x2_5(ssh_oras4)
postprocess(ssh_oras4_regrid)

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
