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
from ninolearn.pathes import infodir, preddir, processeddir
from ninolearn.utils import num_to_month, month_to_num, month_to_season_first, month_to_season_last, pred_filename
from s0_start import start_pred_y, start_pred_m

# =============================================================================
# Loading the predictions
# =============================================================================

lead_times = np.load(join(infodir,'lead_times.npy'))
fn = pred_filename(start_pred_y, start_pred_m)
predictions = pd.read_csv(join(preddir,fn+'_ninolearn.csv'), index_col=0)
seasons = predictions.index.values
mean = predictions['Mean'].values
std = predictions['STD'].values
std_upper = mean + std
std_lower = mean - std

# Load IRI/CPC forecasts to plot along for comparison
IRICPC = np.load(join(preddir,fn+'_iricpc.npy'),allow_pickle=True)
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
plt.grid(True)
plt.ylabel('Nino3.4 SST anomaly ($^\circ$C)',fontsize=11)
plt.yticks(fontsize=10)
plt.title('Model predictions of ENSO from '+str(num_to_month(start_pred_m))+' '+str(start_pred_y),fontsize=13)


# =============================================================================
# Plot IRI/CPC predictions; plot last observations from IRI/CPC or from ONI dataset
# =============================================================================

if plot_iricpc: # IRI/CPC data available
    # Plot last observations
    last_obs_seas_label = IRICPC[0][0:3]
    last_obs_seas = float(IRICPC[0][3:])
    plt.scatter(lead_times[0]-3,last_obs_seas, color='k', zorder=3)
    last_obs_month_label = IRICPC[1][0:3]
    last_obs_month = float(IRICPC[1][3:])
    plt.scatter(lead_times[0]-2,last_obs_month, color='k', zorder=3)
    plt.plot([lead_times[0]-3, lead_times[0]-2], [last_obs_seas,last_obs_month], 'k')
    plt.plot([lead_times[0]-2, lead_times[0]], [last_obs_month,mean[0]], ':k', alpha=0.5)
    
    # Plot IRI/CPC forecasts
    for i in range(2,np.size(IRICPC,0)):
        plt.plot(lead_times, IRICPC[i], color='grey', alpha=0.5)
        plt.plot(lead_times, IRICPC[i], 'o', color='grey', alpha=0.5)
        plt.plot([lead_times[0]-2, lead_times[0]], [last_obs_month,IRICPC[i][0]], ':k', alpha=0.5)
    
    mid_seas = month_to_num(last_obs_month_label)
    mid_seas_label = month_to_season_first(mid_seas)
    ticklabels=np.hstack((last_obs_seas_label,last_obs_month_label,mid_seas_label,seasons))
    
    plt.xlim(lead_times[0]-3, lead_times[-1])
    plt.xticks(np.arange(lead_times[0]-3,lead_times[-1]+1), ticklabels, fontsize=10)
    plt.plot(np.arange(lead_times[0]-3,lead_times[-1]+1), np.zeros(len(lead_times)+3),'k')
    plt.text(lead_times[0]-2.9,plt.gca().get_ylim()[0]+0.1,"OBSERVED",fontsize=10,fontfamily='serif')
    plt.text(lead_times[0]+0.1,plt.gca().get_ylim()[0]+0.1,"FORECAST",fontsize=10,fontfamily='serif')

else: # no IRI/CPC data
    # If the ONI observation from the previous month is available, plot it
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
        plt.scatter(lead_times[0]-3,last_obs, color='k', zorder=3)
        plt.plot([lead_times[0]-3, lead_times[0]], [last_obs, mean[0]], ':k')
        plt.xlim(lead_times[0]-3,lead_times[-1])
        tick1 = month_to_season_last(obs_month)
        if obs_month < 12:
            tick2 = month_to_season_last(obs_month+1)
            if obs_month < 11:
                tick3 = month_to_season_last(obs_month+2)
            else:
                tick3 = month_to_season_last(1)
        else:
            tick2 = month_to_season_last(1)
            tick3 = month_to_season_last(2)
        ticklabels = np.hstack((tick1,tick2,tick3,seasons))
        plt.xticks(np.arange(lead_times[0]-3,lead_times[-1]+1), ticklabels, fontsize=10)
        plt.plot(np.arange(lead_times[0]-3,lead_times[-1]+1), np.zeros(len(lead_times)+3),'k')
    else:
        plt.xlim(lead_times[0], lead_times[-1])
        plt.xticks(lead_times, seasons, fontsize=10)
        plt.plot(lead_times, np.zeros(len(lead_times)),'k')


plt.savefig(join(preddir,fn+'.png'))
plt.savefig(join(preddir,fn+'.pdf'))


print("Step 4 finished, continue to step 5!")