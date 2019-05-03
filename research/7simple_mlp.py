# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import keras.backend as K
from keras.models import Sequential, Model
from keras.layers import Dense, Input
from keras.layers import Dropout, GaussianNoise
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
from keras import regularizers
from keras.layers.core import Lambda
from keras.regularizers import l2

from sklearn.preprocessing import StandardScaler

from ninolearn.IO.read_post import data_reader
from ninolearn.plot.evaluation  import plot_explained_variance
from ninolearn.learn.evaluation import rmse
from ninolearn.learn.mlp import include_time_lag

K.clear_session()

# =============================================================================
# #%% read data
# =============================================================================
reader = data_reader(startdate='1981-01')

nino4 = reader.read_csv('nino4M')
nino34 = reader.read_csv('nino3.4M')
nino12 = reader.read_csv('nino1+2M')
nino3 = reader.read_csv('nino3M')

len_ts = len(nino34)
sc = np.cos(np.arange(len_ts)/12*2*np.pi)
yr =  np.arange(len_ts) % 12
yr3 = np.arange(len_ts) % 36
yr4 = np.arange(len_ts) % 48
yr5 = np.arange(len_ts) % 60


wwv = reader.read_csv('wwv')
network = reader.read_statistic('network_metrics', variable='air',
                           dataset='NCEP', processed="anom")

network_ssh = reader.read_statistic('network_metrics', variable='sshg',
                           dataset='GODAS', processed="anom")

pca_air = reader.read_statistic('pca', variable='air',
                           dataset='NCEP', processed="anom")
pca_u = reader.read_statistic('pca', variable='uwnd',
                           dataset='NCEP', processed="anom")
pca_v = reader.read_statistic('pca', variable='vwnd',
                           dataset='NCEP', processed="anom")


c2 = network['fraction_clusters_size_2']
c3 = network['fraction_clusters_size_3']
c5 = network['fraction_clusters_size_5']
S = network['fraction_giant_component']
H = network['corrected_hamming_distance']
T = network['global_transitivity']
C = network['avelocal_transmissivity']
L = network['average_path_length']
nwt = network['threshold']
pca1_air = pca_air['pca1']
pca2_air = pca_air['pca2']
pca3_air = pca_air['pca3']
pca1_u = pca_u['pca1']
pca2_u = pca_u['pca2']
pca3_u = pca_u['pca3']
pca1_v = pca_v['pca1']
pca2_v = pca_v['pca2']
pca3_v = pca_v['pca3']

c2ssh = network_ssh['fraction_clusters_size_2']

#%% =============================================================================
# # process data
# =============================================================================
time_lag = 12
lead_time = 6
train_frac = 0.67
feature_unscaled = np.stack((nino34.values, c2ssh.values, # nino12.values , nino3.values, nino4.values,
                             wwv.values, sc,   #yr # nwt.values#, c2.values,c3.values, c5.values,
#                            S.values, H.values, T.values, C.values, L.values,
#                            pca1_air.values, pca2_air.values, pca3_air.values,
#                             pca1_u.values, pca2_u.values, pca3_u.values,
#                             pca1_v.values, pca2_v.values, pca3_v.values
                             ), axis=1)


scaler = StandardScaler()
Xorg = scaler.fit_transform(feature_unscaled)

X = Xorg[:-lead_time,:]
futureX = Xorg[-lead_time-time_lag:,:]

X = include_time_lag(X, max_lag=time_lag)
futureX =  include_time_lag(futureX, max_lag=time_lag)


yorg = nino34.values
y = yorg[lead_time + time_lag:]

timey = nino34.index[lead_time + time_lag:]
futuretime = pd.date_range(start='2019-01-01',
                                        end=pd.to_datetime('2019-01-01')+pd.tseries.offsets.MonthEnd(lead_time),
                                        freq='MS')


train_end = int(train_frac * X.shape[0])
trainX, testX = X[:train_end,:], X[train_end:,:]
trainy, testy= y[:train_end], y[train_end:]
traintimey, testtimey = timey[:train_end], timey[train_end:]

#%% =============================================================================
# # neural network
# =============================================================================
inputs = Input(shape=(trainX.shape[1],))
inter = Dropout(0.2)(inputs, training=False)
inter = Dense(50, activation='relu', W_regularizer=l2(0.0))(inter)
inter = Dropout(0.2)(inter, training=False)
outputs = Dense(1, W_regularizer=l2(0.2))(inter)
model = Model(inputs, outputs)

optimizer = Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)


model.compile(loss="mean_squared_error", optimizer=optimizer, metrics=['mse'])

es = EarlyStopping(monitor='val_mean_squared_error',
                          min_delta=0.0,
                          patience=50,
                          verbose=0, mode='auto',
                          restore_best_weights=True)

history = model.fit(trainX, trainy, epochs=500, batch_size=20,verbose=1,
                    shuffle=True, callbacks=[es],
                    validation_data=(testX, testy))

predicttrainy = model.predict(trainX)
predictfuturey = model.predict(futureX)


#%% =============================================================================
# # plot
# =============================================================================
plt.close("all")
plt.subplots(figsize=(12,4))

n_ens = 1000

predict_ens = np.zeros((len(testy),n_ens))
in_or_out = np.zeros((len(testy)))

for i in range(n_ens):
    predict_ens[:,i] = model.predict(testX+ np.random.normal(0, 1, size=testX.shape))[:,0]

predicty_mean = predict_ens.mean(axis=1)
predicty_std = predict_ens.std(axis=1)
predicty_max = predicty_mean + predicty_std
predicty_min = predicty_mean - predicty_std


in_or_out[(testy>predicty_min) & (testy<predicty_max)] = 1
in_frac = np.sum(in_or_out)/len(testy)

score = rmse(testy, predicty_mean)
corr = np.corrcoef(testy, predicty_mean)[0,1]
plt.title(f"{lead_time}-month lead time, RMSE:{round(score,2)}, inside uncertainty: {round(in_frac*100,2)}%")

plt.plot(testtimey,predicty_mean, "b")
plt.fill_between(testtimey,predicty_min,predicty_max ,facecolor='blue', alpha=0.3)

plt.plot(timey, y, "k")
plt.plot(traintimey,predicttrainy, "lime")
plt.plot(futuretime,predictfuturey, "b--")
plt.ylim(-4,4)


plot_explained_variance(testy, predicty_mean, testtimey)
plt.title(f"{lead_time}-month lead time, r:{round(corr,2)}")
plt.subplots()
plt.plot(history.history['val_loss'],label = "val")
plt.plot(history.history['loss'], label= "train")
plt.legend()
