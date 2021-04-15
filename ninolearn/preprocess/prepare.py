"""
This module is a collection of methods that are needed to convert the raw
data to a same format.
"""

import pandas as pd
from os.path import join, exists
from os import mkdir
import numpy as np
from datetime import datetime
import xarray as xr

from ninolearn.IO import read_raw
from ninolearn.pathes import rawdir, processeddir, preddir
from ninolearn.IO.read_processed import data_reader


if not exists(processeddir):
    print("make a data directory at %s" % processeddir)
    mkdir(processeddir)


def season_to_month(season):
    """
    translates a 3-month season string to the corresponding integer of the
    last month of the season (to ensure not to include any future information
    when predictions are made later with this data)

    :type season: string
    :param season: Season represented by three letters such as 'DJF'
    """
    switcher = {'DJF': 2,
                'JFM': 3,
                'FMA': 4,
                'MAM': 5,
                'AMJ': 6,
                'MJJ': 7,
                'JJA': 8,
                'JAS': 9,
                'ASO': 10,
                'SON': 11,
                'OND': 12,
                'NDJ': 1,
                }

    return switcher[season]

def season_shift_year(season):
    """
    when the function .season_to_month() is applied the year related to
    NDJ needs to be shifted by 1.

    :type season: string
    :param season: Season represented by three letters such as 'DJF'
    """
    switcher = {'DJF': 0,
                'JFM': 0,
                'FMA': 0,
                'MAM': 0,
                'AMJ': 0,
                'MJJ': 0,
                'JJA': 0,
                'JAS': 0,
                'ASO': 0,
                'SON': 0,
                'OND': 0,
                'NDJ': 1,
                }

    return switcher[season]

def prep_oni():
    """
    Add a time axis corresponding to the first day of the last month of a
    3-month season. For example: DJF 2019 becomes 2019-02-01. Further, rename
    some axis.
    """
    print("Prepare ONI timeseries.")
    data = read_raw.oni()

    df = ({'year': data.YR.values + data.SEAS.apply(season_shift_year).values,
           'month': data.SEAS.apply(season_to_month).values,
           'day': data.YR.values/data.YR.values})
    dti = pd.to_datetime(df)

    data.index = dti
    data.index.name = 'time'
    data = data.rename(index=str, columns={'ANOM': 'anom'})
    data.to_csv(join(processeddir, f'oni.csv'))

def prep_nino_month(index="3.4", detrend=False):
    """
    Add a time axis corresponding to the first day of the central month.
    """
    print("Prepare monthly Nino3.4 timeseries.")
    period ="M"

    rawdata = read_raw.nino_anom(index=index, period=period, detrend=detrend)
    rawdata = rawdata.rename(index=str, columns={'ANOM': 'anomNINO1+2',
                                                  'ANOM.1': 'anomNINO3',
                                                  'ANOM.2': 'anomNINO4',
                                                  'ANOM.3': 'anomNINO3.4'})

    dftime = ({'year': rawdata.YR.values,
            'month': rawdata.MON.values,
            'day': rawdata.YR.values/rawdata.YR.values})
    dti = pd.to_datetime(dftime)

    data = pd.DataFrame(data=rawdata[f"anomNINO{index}"])

    data.index = dti
    data.index.name = 'time'
    data = data.rename(index=str, columns={f'anomNINO{index}': 'anom'})

    filename = f"nino{index}{period}"

    if detrend:
        filename = ''.join(filename, "detrend")
    filename = ''.join((filename,'.csv'))

    data.to_csv(join(processeddir, filename))

def prep_wwv(cardinal_direction=""):
    """
    Add a time axis corresponding to the first day of the central month of a
    3-month season. For example: DJF 2019 becomes 2019-01-01. Further, rename
    some axes.
    """
    print(f"Prepare WWV {cardinal_direction} timeseries.")
    data = read_raw.wwv_anom(cardinal_direction=cardinal_direction)

    df = ({'year': data.date.astype(str).str[:4],
           'month': data.date.astype(str).str[4:],
           'day': data.date/data.date})
    dti = pd.to_datetime(df)

    data.index = dti
    data.index.name = 'time'
    data = data.rename(index=str, columns={'Anomaly': 'anom'})
    data.to_csv(join(processeddir, f'wwv{cardinal_direction}.csv'))

def prep_K_index():
    """
    function that edits the Kirimati index from Bunge and Clarke (2014)
    """
    print(f"Prepare K index.")
    data = read_raw.K_index()
    data.index.name = 'time'
    data.name = 'anom'
    data.to_csv(join(processeddir, f'kindex.csv'), header=True)

def prep_wwv_proxy():
    """
    Make a wwv proxy index that uses the K-index from Bunge and Clarke (2014)
    for the time period between 1955 and 1979
    """
    print(f"Prepare WWV proxy.")
    wwv_raw = pd.read_csv(join(rawdir, 'wwv.dat'),
                       delim_whitespace=True, header=4)
    wwv_end = str(wwv_raw['date'].iloc[-1])
    endyr = wwv_end[:4]
    endmth = wwv_end[4:]
    
    reader_wwv = data_reader(startdate='1980-01', enddate=endyr+'-'+endmth)
    wwv = reader_wwv.read_csv('wwv')

    reader_kindex = data_reader(startdate='1955-01', enddate='1979-12')
    kindex = reader_kindex.read_csv('kindex') * 10e12

    wwv_proxy = kindex.append(wwv)
    wwv_proxy.to_csv(join(processeddir, f'wwv_proxy.csv'), header=True)


def prep_iod():
    """
    Prepare the IOD index dataframe
    """
    print("Prepare IOD timeseries.") 
    
    data = read_raw.iod()
    data = data.T.unstack()
    data = data.replace(-9999, np.nan)
    data = data.dropna()
    enddate = data.index[-1]
    endyr = str(enddate[0])
    if enddate[1] < 10:
        endmth = '0'+str(enddate[1])
    else:
        endmth = str(enddate[1])

    dti = pd.date_range(start='1870-01-01', end=endyr+'-'+endmth+'-01', freq='MS')

    df = pd.DataFrame(data=data.values,index=dti, columns=['anom'])
    df.index.name = 'time'

    df.to_csv(join(processeddir, 'iod.csv'))
    
    
def prep_dmi():
    """
    Prepare the DMI dataframe
    """
    print("Prepare DMI timeseries.")
    
    data = read_raw.dmi()
    time = data.variables['time'][:]
    dmi = data.variables['diff'][:]
    
    dti = pd.date_range(start='1854-01-01', periods=len(time), freq='MS')
    df = pd.DataFrame(data=dmi,index=dti, columns=['anom'])
    df.index.name = 'time'
    df = df.dropna()
    
    df.to_csv(join(processeddir, 'dmi.csv'))
    

def calc_warm_pool_edge():
    """
    calculate the warm pool edge
    """
    reader = data_reader(startdate='1948-01', enddate='2020-10',lon_min=120, lon_max=290) # enddate: was 2018-12
    sst = reader.read_netcdf('sst', dataset='ERSSTv5', processed='')

    sst_eq = sst.loc[dict(latitude=0)]
    warm_pool_edge = np.zeros(sst_eq.shape[0])
    indeces = np.zeros(sst_eq.shape[0])

    # TODO  not very efficent
    for i in range(sst_eq.shape[0]):
        index = np.argwhere(sst_eq[i].values>28.).max()
        indeces[i] = index

        slope = sst_eq[i, index] - sst_eq[i, index-1]

        intercept28C = (sst_eq[i, index] - 28.) * slope + index

        warm_pool_edge[i] = intercept28C * 2.5 * 111.321

    df = pd.DataFrame(data=warm_pool_edge,index=sst.time.values, columns=['total'])
    df.index.name = 'time'

    df.to_csv(join(processeddir, 'wp_edge.csv'))


def prep_other_forecasts(month,year):
    """
    Extract IRI/CPC forecast for desired period
    """
    print("Prepare IRI/CPC forecast data.")
    IRICPC = []
    f = open(join(rawdir,"other_forecasts.txt"), "r")
    go = True
    while go:
        line = f.readline()
        if line == 'Forecast issued '+month+' '+year+'\n':
            go = False
            f.readline() # first/last month info
            last_obs = f.readline() # last obs info
            last_obs_info = last_obs[16:].strip()
            last_obs_info = last_obs_info.replace(" ","")
            last_obs_seas = last_obs_info[0:8]
            last_obs_month = last_obs_info[8:]
            IRICPC.append(last_obs_seas)
            IRICPC.append(last_obs_month)
            read_forecast = True
            while read_forecast:
                line = f.readline()
                if line == 'end\n' or line == '\n':
                    read_forecast = False
                    break
                fc = np.zeros(9) # forecasts are made for 9-month lead times
                for i in range(9):
                    fc[i] = float(line[4*i:4*(i+1)])*0.01
                    fc = np.where(fc==-9.99, np.nan, fc)
                IRICPC.append(fc)
            print('IRI/CPC forecasts saved')    
        if not line:
            print('IRI/CPC forecast not found for desired period')
            break
    f.close()
    return IRICPC


