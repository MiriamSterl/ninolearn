"""
STEP 4: PLOT [OPTIONAL]
Plotting the predictions.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from s0_start import start_pred_y, start_pred_m

predictions = pd.read_csv('predictions.csv', index_col=0)

# TODO: de rest hieronder opruimen
if start_pred_m < 10:
    filename = 'predictions_'+str(start_pred_y)+'_0'+str(start_pred_m)
else:
    filename = 'predictions_'+str(start_pred_y)+'_'+str(start_pred_m)

# TODO: folder
lead_times = np.load('lead_times.npy')
predictions = np.load(filename+'.npy')
mean = predictions[0]
std = predictions[1]
std_upper = mean + std
std_lower = mean - std

#%%

# TODO this is bad code!! Foei (txt bestandje ook maar met de hand gemanipuleerd)
f = open("iricpc.txt", "r")
forecasts = np.zeros((26,9))
for i in np.arange(0,26):
    line = f.readline()
    values = line.split()
    for j in np.arange(0,9):
        forecasts[i,j] = int(values[j])*0.01
forecasts = np.where(forecasts==-9.99,np.nan,forecasts)
f.close()    



#%%

# TODO: check definition 3-month periods vs month.
# Now it is: 3-month per corresponds with first month of that per.
# Other possibility: take averages. --> this is it

def month_to_season(month):
    """
    Translates a month (int between 1 and 12) to a string denoting the 3-month
    period starting with the given month.
    """
    # TODO: possibly different if 3-month periods defined differently.
    switcher = {1: 'JFM',
                2: 'FMA',
                3: 'MAM',
                4: 'AMJ',
                5: 'MJJ',
                6: 'JJA',
                7: 'JAS',
                8: 'ASO',
                9: 'SON',
                10: 'OND',
                11: 'NDJ',
                12: 'DJF'}
    return switcher[month]
# TODO: perhaps move this to utils

seasons = np.empty(len(mean), dtype=object)
for i in np.arange(len(mean)):
    seasons[i] = month_to_season(start_pred_m+i)


#%%
# Even gekunsteld time axes gelijk maken
# lead_times = np.append([1], lead_times)
# seasons = np.append(['JFM'], seasons)
# mean = np.append([np.nan], mean)
# std_upper = np.append([np.nan], std_upper)
# std_lower = np.append([np.nan], std_lower)
# forecasts = np.hstack((forecasts, np.zeros((26,1))*np.nan))


#%%
plt.figure()
for i in np.arange(0,26):
    plt.plot(lead_times, forecasts[i,:], color='grey', alpha=0.5)
    plt.plot(lead_times, forecasts[i,:], 'o', color='grey', alpha=0.5)
plt.plot(lead_times, np.zeros(len(lead_times)),'k')
plt.plot(lead_times,mean, 'b')
plt.plot(lead_times,mean, 'ob')
plt.plot(lead_times, std_upper, '--b')
plt.plot(lead_times, std_lower, '--b')
plt.fill_between(lead_times, std_lower, std_upper, facecolor='b', alpha=0.2)
plt.grid(True)
plt.ylabel('Nino3.4 SST anomaly ($^\circ$C)')
plt.xticks(lead_times, seasons)
plt.title('Model predictions of ENSO from Jan '+str(start_pred_y)) 
# TODO: also make starting month in title from start_pred_m, move to utils
# TODO: get IRI/CPC data to compare. Best to be done already earlier in download.




