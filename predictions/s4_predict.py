"""
STEP 4: PREDICT
The GDNN models are used to make predictions.
"""
import numpy as np
#from pickle import load

from ninolearn.pathes import modeldir
from ninolearn.learn.models.dem import DEM
from ninolearn.learn.fit import decades # TODO: update decades
from ninolearn.utils import include_time_lag

from s0_start import start_pred_y, start_pred_m


#%%
# =============================================================================
# Getting feature vector
# =============================================================================

#scalerX = load(open('scalerX.pkl', 'rb'))
Xorg = np.load('Xorg.npy') # TODO: folder
# include values of 3 and 6 months previously
n_lags = 3
step = 3
X = include_time_lag(Xorg, n_lags=n_lags, step=step)
X = X[-1:,:] # now use only the latest observation to produce forecast


#%%
# =============================================================================
# For each lead time, load ensemble of models and make prediction
# =============================================================================

lead_times = np.load('lead_times.npy') # TODO: folder
predictions = np.zeros((2,len(lead_times))) # first row: mean, second row: std

for i in np.arange(len(lead_times)):
    print("Lead time "+str(lead_times[i])+" months")
    dem = DEM(layers=1, neurons = 32, dropout=0.05, noise_in=0.0, noise_sigma=0.,
                       noise_mu=0., l1_hidden=0.0, l2_hidden=0.,
                       l1_mu=0, l2_mu=0., l1_sigma=0,
                       l2_sigma=0.0, lr=0.01, batch_size=100,
                       epochs=5000, n_segments=5, n_members_segment=3, patience=25,
                       activation='tanh',
                       verbose=0, pdf="normal", name="gdnn_ex_pca")
    for j in decades[:-1]:
        dem.load(location=modeldir, dir_name = 'gdnn_ex_pca_decade'+str(j)+'_lead'+str(lead_times[i]))
    pred = dem.predict(X)
    predictions[0,i] = pred[0][0]
    predictions[1,i] = pred[1][0]

if start_pred_m < 10:
    filename = 'predictions_'+str(start_pred_y)+'_0'+str(start_pred_m)
else:
    filename = 'predictions_'+str(start_pred_y)+'_'+str(start_pred_m)
np.save(filename, predictions)



