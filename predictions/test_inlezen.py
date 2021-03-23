# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 15:57:18 2021

@author: miria
"""
testline1 = "Obs Nino3.4 SST:  JAS-0.64 Sep-0.95\n"
testline2 = "Obs Nino3.4 SST:  JFM 0.72  Mar 0.98\n"

info = testline1[18:]
#info = testline2[18:]

# Season label
last_obs_seas_label = info[0:3]
#last_obs_seas_label2 = info2[0:3]

# check of volgende een - is
if info[3] == '-':
    last_obs_seas = float(info[3:8])
else:
    last_obs_seas = float(info[4:8])

# spaties overslaan hup


# Month label

# check of volgende een - is

# month getal

# en stop dan maar in logisch format zodat onderstaande plotcode altijd werkt


# last_obs_seas_label = IRICPC[0][0:3]
#     last_obs_seas = float(IRICPC[0][3:])
#     plt.scatter(lead_times[0]-3,last_obs_seas, color='k', zorder=3)
#     last_obs_month_label = IRICPC[1][0:3]
#     last_obs_month = float(IRICPC[1][3:])