"""
STEP 5: PLOT
Plotting the predictions.
"""

import numpy as np
import matplotlib.pyplot as plt
from s0_start import start_pred_y, start_pred_m

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

# TODO: check definition 3-month periods vs month.
# Now it is: 3-month per corresponds with first month of that per.
# Other possibility: take averages. 

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
# TODO: merk op: begint nu bij FMA, huidige IRI begint bij JFM. Wordt vast binnenkort geüpdate.
plt.figure()
plt.plot(lead_times, np.zeros(len(lead_times)),'k')
plt.plot(lead_times,mean, 'b')
plt.plot(lead_times,mean, 'ob')
plt.plot(lead_times, std_upper, '--b')
plt.plot(lead_times, std_lower, '--b')
plt.fill_between(lead_times, std_lower, std_upper, facecolor='b', alpha=0.6)
plt.grid(True)
plt.ylabel('Nino3.4 SST anomaly ($^\circ$C)')
plt.xticks(lead_times, seasons)
plt.title('Model predictions of ENSO from Feb '+str(start_pred_y)) 
# TODO: also make starting month in title from start_pred_m, move to utils




