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
from datetime import datetime
from ninolearn.pathes import infodir, processeddir, preddir
from ninolearn.utils import num_to_month, month_to_season
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


# =============================================================================
# Plotting the predictions
# =============================================================================

plt.figure(figsize=(8,5))
plt.plot(lead_times, np.zeros(len(lead_times)),'k')
plt.plot(lead_times,mean, 'b')
plt.plot(lead_times,mean, 'ob', zorder=3)
plt.plot(lead_times, std_upper, '--b')
plt.plot(lead_times, std_lower, '--b')
plt.fill_between(lead_times, std_lower, std_upper, facecolor='b', alpha=0.2)
plt.grid(True)
plt.ylabel('Nino3.4 SST anomaly ($^\circ$C)',fontsize=11)
plt.yticks(fontsize=10)
plt.title('Model predictions of ENSO from '+str(num_to_month(start_pred_m))+' '+str(start_pred_y),fontsize=13)


# If the ONI observation from the previous month is available, plot it as well
# oni_obs = pd.read_csv(join(processeddir, 'oni.csv'))
# last_date_str = oni_obs.iloc[-1]['time']
# last_date = datetime.strptime(last_date_str,'%Y-%m-%d %H:%M:%S')
# plot_obs = False
# # TODO: deze if kan mooier!
# if current_month > 1:
#     if last_date.year == current_year and last_date.month == current_month-1: 
#         plot_obs = True
# else:
#     if last_date.year == current_year-1 and last_date.month == 12:
#         plot_obs = True
# if plot_obs:
#     last_obs = oni_obs.iloc[-1]['anom']
#     plt.plot([lead_times[0]-2, lead_times[0]], [last_obs, mean[0]], ':k')
#     plt.scatter(lead_times[0]-2,last_obs, color='k', zorder=3)
#     plt.xlim(lead_times[0]-2,lead_times[-1])
#     tick1 = num_to_month(last_date.month)
#     tick2 = month_to_season(last_date.month)
#     ticklabels = np.hstack((tick1,tick2,seasons))
#     plt.xticks(np.arange(lead_times[0]-2,lead_times[-1]+1), ticklabels, fontsize=10)
#     plt.text(lead_times[0]-1.9,plt.gca().get_ylim()[0]+0.1,"OBSERVED",fontsize=10,fontfamily='serif')
#     plt.text(lead_times[0]+0.1,plt.gca().get_ylim()[0]+0.1,"FORECAST",fontsize=10,fontfamily='serif')
# else:
#     plt.xlim(lead_times[0], lead_times[-1])
#     plt.xticks(lead_times, seasons, fontsize=10)


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
    plt.plot([lead_times[0]-2, lead_times[0]], [last_obs, mean[0]], ':k')
    plt.scatter(lead_times[0]-2,last_obs, color='k', zorder=3)
    plt.xlim(lead_times[0]-2,lead_times[-1])
    tick1 = num_to_month(obs_month)
    tick2 = month_to_season(obs_month)
    ticklabels = np.hstack((tick1,tick2,seasons))
    plt.xticks(np.arange(lead_times[0]-2,lead_times[-1]+1), ticklabels, fontsize=10)
    plt.text(lead_times[0]-1.9,plt.gca().get_ylim()[0]+0.1,"OBSERVED",fontsize=10,fontfamily='serif')
    plt.text(lead_times[0]+0.1,plt.gca().get_ylim()[0]+0.1,"FORECAST",fontsize=10,fontfamily='serif')
else:
    plt.xlim(lead_times[0], lead_times[-1])
    plt.xticks(lead_times, seasons, fontsize=10)


plt.savefig(join(preddir,filename+'.png'))
plt.savefig(join(preddir,filename+'.pdf'))


print("Step 4 finished, continue to step 5!")