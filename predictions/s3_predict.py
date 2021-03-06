"""
STEP 3: PREDICT
The GDNN models are used to make predictions.
"""
from s0_start import basedir
import sys  
sys.path.append(basedir)

import numpy as np
import pandas as pd
from os.path import join

from ninolearn.utils import month_to_season_first, print_header, include_time_lag, pred_filename
from ninolearn.pathes import modeldir, infodir, preddir
from ninolearn.learn.models.dem import DEM
from ninolearn.learn.fit import decades

from s0_start import start_pred_y, start_pred_m


# =============================================================================
# Getting feature vector
# =============================================================================

Xorg = np.load(join(infodir,'Xorg.npy'))
# include values of 3 and 6 months previously
n_lags = 3
step = 3
X = include_time_lag(Xorg, n_lags = n_lags, step=step)
X = X[-1:,:] # now use only the latest observation to produce forecast


# =============================================================================
# For each lead time, load ensemble of models and make prediction
# =============================================================================

lead_times = np.load(join(infodir,'lead_times.npy'))
predictions = np.zeros((2,len(lead_times))) # first row: mean, second row: std

print_header("Making predictions")

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
    predictions[0,i] = pred[0][0] # mean
    predictions[1,i] = pred[1][0] # std


# =============================================================================
# Save predictions
# =============================================================================

# Translate months to 3-month seasons centered around central month
seasons = np.empty(len(predictions[0,:]), dtype=object)
for i in np.arange(len(predictions[0,:])):
    if start_pred_m+i<13:
        seasons[i] = month_to_season_first(start_pred_m+i)
    else:
        seasons[i] = month_to_season_first((start_pred_m+i)%12)
np.save(join(infodir,'seasons'), seasons)

# Save predictions as DataFrame
df = pd.DataFrame({'Mean': predictions[0,:], 'STD': predictions[1,:]}, index = seasons)
df.index.name = 'Season'

fn = pred_filename(start_pred_y, start_pred_m)+'_ninolearn.csv'
df.to_csv(join(preddir,fn))

print("Predictions saved!")

print("\nStep 3 finished, continue to step 4 or step 5!")