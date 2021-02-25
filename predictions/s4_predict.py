"""
STEP 4: PREDICT
The GDNN models are used to make predictions.
"""
import numpy as np
#from pickle import load

from ninolearn.pathes import modeldir
from ninolearn.learn.models.dem import DEM
from ninolearn.learn.fit import decades # TODO: update decades --> perhaps in start already

from s0_start import start_pred_y, start_pred_m


#%%
# =============================================================================
# Getting feature vector
# =============================================================================

#scalerX = load(open('scalerX.pkl', 'rb'))
X = np.load('features.npy') # TODO: folder
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

#%%
# TODO: dit allemaal ordenen
from scipy.ndimage.filters import uniform_filter1d

pred_seasons_mean = uniform_filter1d(predictions[0,:], size=3)
pred_seasons_mean = pred_seasons_mean[1:-1] # TODO: CHECK! Goede lengte?
pred_seasons_std = uniform_filter1d(predictions[1,:], size=3)
pred_seasons_std = pred_seasons_std[1:-1] # TODO: CHECK! Goede lengte?


# TODO: maybe use generateFileName or make something like that
# TODO: not necessary later --> move this to saving the dataframe
if start_pred_m < 10:
    filename = 'predictions_'+str(start_pred_y)+'_0'+str(start_pred_m)
else:
    filename = 'predictions_'+str(start_pred_y)+'_'+str(start_pred_m)
np.save(filename, predictions)


def month_to_season(month):
    """
    Translates a month (int between 1 and 12) to a string denoting the 3-month
    period centered around the given month.
    """
    switcher = {1: 'DJF',
                2: 'JFM',
                3: 'FMA',
                4: 'MAM',
                5: 'AMJ',
                6: 'MJJ',
                7: 'JJA',
                8: 'JAS',
                9: 'ASO',
                10: 'SON',
                11: 'OND',
                12: 'NDJ'}
    return switcher[month]
# TODO: perhaps move this to utils


seasons = np.empty(len(pred_seasons_mean), dtype=object)
for i in np.arange(len(pred_seasons_mean)):
    seasons[i] = month_to_season(start_pred_m+i)

import pandas as pd

df = pd.DataFrame({'Mean': pred_seasons_mean, 'STD': pred_seasons_std}, index = seasons)
df.index.name = 'Season'
#%%
df.to_csv('predictions.csv') # TODO: folder + naam!! Zoals boven

