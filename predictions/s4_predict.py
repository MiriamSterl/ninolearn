"""
The GDNN models are used to make predictions.
"""
import numpy as np
from pickle import load
#from start import year, month

from ninolearn.pathes import modeldir
from ninolearn.learn.models.dem import DEM
from ninolearn.learn.fit import decades
from ninolearn.IO.read_processed import data_reader
from ninolearn.utils import include_time_lag

#%%
# =============================================================================
# # Loading ensemble of models
# =============================================================================
dem = DEM(layers=1, neurons = 32, dropout=0.05, noise_in=0.0, noise_sigma=0.,
                   noise_mu=0., l1_hidden=0.0, l2_hidden=0.,
                   l1_mu=0, l2_mu=0., l1_sigma=0,
                   l2_sigma=0.0, lr=0.01, batch_size=100,
                   epochs=5000, n_segments=5, n_members_segment=3, patience=25,
                   activation='tanh',
                   verbose=0, pdf="normal", name="gdnn_ex_pca")

# TODO: for all lead times, + update decades
for i in decades[:-1]:
    dem.load(location=modeldir, dir_name = 'gdnn_ex_pca_decade'+str(i)+'_lead0')

#%%
# =============================================================================
# # Getting feature vector
# =============================================================================
f = open("enddate.txt", "r")
endyr = f.readline()
endmth = f.readline()
date = endyr+'-'+endmth
    
reader = data_reader(startdate=date, enddate=date)

# indices
oni = reader.read_csv('oni')
iod = reader.read_csv('iod')
wwv = reader.read_csv('wwv_proxy')

# seasonal cycle
month = str(endmth)-1
cos = np.cos(month/12*2*np.pi)

# wind stress
taux = reader.read_netcdf('taux', dataset='NCEP', processed='anom')

taux_WP = taux.loc[dict(lat=slice(2.5,-2.5), lon=slice(120, 160))]
taux_WP_mean = taux_WP.mean(dim='lat').mean(dim='lon')

# process features
feature_unscaled = np.stack((oni,
                             wwv,
                             iod,
                             cos,
                             taux_WP_mean
                             ), axis=1)

# scale each feature
scalerX = load(open('scalerX.pkl', 'rb'))
Xorg = scalerX.fit_transform(feature_unscaled)

# set nans to 0.
Xorg = np.nan_to_num(Xorg)
X = Xorg # dit kan later natuurlijk weg, maar even afwachten of de onderstaande dingen inderdaad weg mogen

# time lag
n_lags = 3
step = 3

# shift such that lead time corresponds to the definition of lead time
shift = 3

# arange the feature array
#X = Xorg[:-lead_time-shift,:]
#X = include_time_lag(X, n_lags=n_lags, step=step)

#%%

test = dem.predict(X)















