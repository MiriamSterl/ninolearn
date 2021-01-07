from start import filedir
import sys  
sys.path.append(filedir)

import numpy as np
from sklearn.preprocessing import StandardScaler

from ninolearn.utils import include_time_lag
from ninolearn.IO.read_processed import data_reader
from ninolearn.learn.models.dem import DEM

from ninolearn.learn.fit import cross_training


def pipeline(lead_time,  return_persistance=False):
    """
    Data pipeline for the processing of the data before the Deep Ensemble
    is trained.

    :type lead_time: int
    :param lead_time: The lead time in month.

    :type return_persistance: boolean
    :param return_persistance: Return as the persistance as well.

    :returns: The feature "X" (at observation time), the label "y" (at lead
    time), the target season "timey" (least month) and if selected the
    label at observation time "y_persistance". Hence, the output comes as:
    X, y, timey, y_persistance.
    """
    reader = data_reader(startdate='1960-01', enddate='2017-12') # UPDATEABLE!

    # indices
    oni = reader.read_csv('oni')

    iod = reader.read_csv('iod')
    wwv = reader.read_csv('wwv_proxy')

    # seasonal cycle
    cos = np.cos(np.arange(len(oni))/12*2*np.pi)

    # network metrics
    network_ssh = reader.read_statistic('network_metrics', variable='zos', dataset='ORAS4', processed="anom")
    H_ssh = network_ssh['corrected_hamming_distance']

    # wind stress
    taux = reader.read_netcdf('taux', dataset='NCEP', processed='anom')

    taux_WP = taux.loc[dict(lat=slice(2.5,-2.5), lon=slice(120, 160))]
    taux_WP_mean = taux_WP.mean(dim='lat').mean(dim='lon')

    # time lag
    n_lags = 3
    step = 3

    # shift such that lead time corresponds to the definition of lead time
    shift = 3

    # process features
    feature_unscaled = np.stack((oni,
                                 wwv,
                                 iod,
                                 cos,
                                 H_ssh,
                                 taux_WP_mean
                                 ), axis=1)

    # scale each feature
    scalerX = StandardScaler()
    Xorg = scalerX.fit_transform(feature_unscaled)

    # set nans to 0.
    Xorg = np.nan_to_num(Xorg)

    # arange the feature array
    X = Xorg[:-lead_time-shift,:]
    X = include_time_lag(X, n_lags=n_lags, step=step)

    # arange label
    yorg = oni.values
    y = yorg[lead_time + n_lags*step + shift:]

    # get the time axis of the label
    timey = oni.index[lead_time + n_lags*step + shift:]

    if return_persistance:
        y_persistance = yorg[n_lags*step: - lead_time - shift]
        return X, y, timey, y_persistance

    else:
        return X, y, timey

if __name__=="__main__":
    cross_training(DEM, pipeline, 1,
                   layers=1, neurons = 32, dropout=0.05, noise_in=0.0, noise_sigma=0.,
                   noise_mu=0., l1_hidden=0.0, l2_hidden=0.,
                   l1_mu=0, l2_mu=0., l1_sigma=0,
                   l2_sigma=0.0, lr=0.01, batch_size=100,
                   epochs=5000, n_segments=5, n_members_segment=3, patience=25,
                   activation='tanh',
                   verbose=0, pdf="normal", name="gdnn_ex_pca")