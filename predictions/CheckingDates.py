"""
Checking dates in datasets
Inspiration from ninolearn/IO/read_processed.py
"""
import numpy as np
import pandas as pd
import xarray as xr
#from netCDF4 import Dataset

#%% ===========================================================================
# Checking in RAW data sets
# =============================================================================
# iod, oni: txt
# wwv: dat
# uwnd: nc

iod_raw = pd.read_csv('iod.txt',
                       delim_whitespace=True, header=None, skiprows=1, skipfooter=7,
                       index_col=0, engine='python')
iod_raw = iod_raw.T.unstack()
iod_raw = iod_raw.replace(-9999,np.nan)
iod_raw = iod_raw.dropna()
iod_end = iod_raw.index[-1]
iod_endyr = iod_end[0]
iod_endmth = iod_end[1]

#%%
wwv = pd.read_csv('wwv.dat',
                       delim_whitespace=True, header=4)
wwv_end = str(wwv['date'].iloc[-1])
wwv_endyr = wwv_end[:4]
wwv_endmth = wwv_end[4:]




#%% ===========================================================================
# Checking in PROCESSED data sets
# =============================================================================
# TODO: put correct directory names
oni = pd.read_csv('oni.csv',index_col=0, parse_dates=True)
wwv = pd.read_csv('wwv_proxy.csv',index_col=0, parse_dates=True)
iod_nan = pd.read_csv('iod.csv',index_col=0, parse_dates=True)
iod = iod_nan.dropna()
taux = xr.open_dataarray('taux_NCEP_anom.nc')

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



