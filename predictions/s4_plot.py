"""
STEP 4: PLOT [OPTIONAL]
Plotting the predictions.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from os.path import join
from ninolearn.pathes import infodir
from ninolearn.utils import num_to_month
from s0_start import start_pred_y, start_pred_m

# =============================================================================
# Loading the predictions
# =============================================================================

lead_times = np.load(join(infodir,'lead_times.npy'))[:-2]
if start_pred_m < 10:
    filename = 'predictions_'+str(start_pred_y)+'_0'+str(start_pred_m)+'.csv'
else:
    filename = 'predictions_'+str(start_pred_y)+'_'+str(start_pred_m)+'.csv'
predictions = pd.read_csv(filename, index_col=0)
seasons = predictions.index.values
mean = predictions['Mean'].values
std = predictions['STD'].values
std_upper = mean + std
std_lower = mean - std



# =============================================================================
# Plotting the prediction
# =============================================================================

# TODO: also include last observation (as in IRI plume)
plt.figure()
plt.plot(lead_times, np.zeros(len(lead_times)),'k')
plt.plot(lead_times,mean, 'b')
plt.plot(lead_times,mean, 'ob')
plt.plot(lead_times, std_upper, '--b')
plt.plot(lead_times, std_lower, '--b')
plt.fill_between(lead_times, std_lower, std_upper, facecolor='b', alpha=0.2)
plt.grid(True)
plt.ylabel('Nino3.4 SST anomaly ($^\circ$C)')
plt.xticks(lead_times, seasons)
plt.title('Model predictions of ENSO from '+str(num_to_month(start_pred_m))+' '+str(start_pred_y))


