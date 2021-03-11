"""
STEP 4: PLOT [OPTIONAL]
Plotting the predictions.
"""
from s0_start import basedir
import sys  
sys.path.append(basedir)

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from os.path import join
from ninolearn.pathes import infodir, processeddir, preddir
from ninolearn.utils import num_to_month, month_to_season_last
from s0_start import start_pred_y, start_pred_m

# =============================================================================
# Loading the predictions
# =============================================================================

lead_times = np.load(join(infodir,'lead_times.npy'))[:-2]
if start_pred_m < 10:
    filename = 'predictions_'+str(start_pred_y)+'_0'+str(start_pred_m)
else:
    filename = 'predictions_'+str(start_pred_y)+'_'+str(start_pred_m)
predictions = pd.read_csv(join(preddir,filename+'.csv'), index_col=0)
seasons = predictions.index.values
mean = predictions['Mean'].values
std = predictions['STD'].values
std_upper = mean + std
std_lower = mean - std

# Load IRI/CPC forecasts to plot along for comparison
IRICPC = np.load(join(processeddir,'IRICPC.npy'))
if len(IRICPC)>0:
    plot_iricpc = True


# =============================================================================
# Plotting the predictions
# =============================================================================

plt.figure(figsize=(8,5))
plt.plot(lead_times,mean, 'b')
plt.plot(lead_times,mean, 'ob', zorder=3)
plt.plot(lead_times, std_upper, '--b')
plt.plot(lead_times, std_lower, '--b')
plt.fill_between(lead_times, std_lower, std_upper, facecolor='b', alpha=0.2)
if plot_iricpc:
    for i in range(np.size(IRICPC,0)):
        plt.plot(lead_times, IRICPC[i,:], color='grey', alpha=0.5)
        plt.plot(lead_times, IRICPC[i,:], 'o', color='grey', alpha=0.5)
plt.grid(True)
plt.ylabel('Nino3.4 SST anomaly ($^\circ$C)',fontsize=11)
plt.yticks(fontsize=10)
plt.title('Model predictions of ENSO from '+str(num_to_month(start_pred_m))+' '+str(start_pred_y),fontsize=13)


# If the ONI observation from the previous month is available, plot it as well
oni_obs = pd.read_csv(join(processeddir, 'oni.csv'))
if start_pred_m > 1:
    obs_year = start_pred_y
    obs_month = start_pred_m - 1
else:
    obs_year = start_pred_y - 1
    obs_month = 12

if obs_month < 10:
    obs_date = str(obs_year)+'-0'+str(obs_month)+'-01 00:00:00'
else:
   obs_date = str(obs_year)+'-'+str(obs_month)+'-01 00:00:00' 
   
obs_index = oni_obs.loc[oni_obs['time']==obs_date].index
if len(obs_index)==1:
    last_obs = oni_obs.iloc[obs_index]['anom']
    plt.scatter(lead_times[0]-2,last_obs, color='k', zorder=3)
    plt.plot([lead_times[0]-2, lead_times[0]], [last_obs, mean[0]], ':k')
    if plot_iricpc:
        for i in range(np.size(IRICPC,0)):
            plt.plot([lead_times[0]-2, lead_times[0]], [last_obs,IRICPC[i,0]], ':k', alpha=0.5)
    plt.xlim(lead_times[0]-2,lead_times[-1])
    tick1 = month_to_season_last(obs_month)
    if obs_month < 12:
        tick2 = month_to_season_last(obs_month+1)
    else:
        tick2 = month_to_season_last(1)
    ticklabels = np.hstack((tick1,tick2,seasons))
    plt.xticks(np.arange(lead_times[0]-2,lead_times[-1]+1), ticklabels, fontsize=10)
    plt.text(lead_times[0]-1.9,plt.gca().get_ylim()[0]+0.1,"OBSERVED",fontsize=10,fontfamily='serif')
    plt.text(lead_times[0]+0.1,plt.gca().get_ylim()[0]+0.1,"FORECAST",fontsize=10,fontfamily='serif')
    plt.plot(np.arange(lead_times[0]-2,lead_times[-1]+1), np.zeros(len(lead_times)+2),'k')
else:
    plt.xlim(lead_times[0], lead_times[-1])
    plt.xticks(lead_times, seasons, fontsize=10)
    plt.plot(lead_times, np.zeros(len(lead_times)),'k')


plt.savefig(join(preddir,filename+'.png'))
plt.savefig(join(preddir,filename+'.pdf'))


print("Step 4 finished, continue to step 5!")