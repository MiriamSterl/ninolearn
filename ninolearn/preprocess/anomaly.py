"""
This module contains a bunch of mehtods to compute seasonal anomalies.

Currently the reference period is 1981-2010.
"""

from os.path import join, exists
import xarray as xr
import pandas as pd

from ninolearn.pathes import processeddir
from ninolearn.utils import generateFileName, small_print_header

# =============================================================================
# # ===========================================================================
# # Pre-Computation
# # ===========================================================================
# =============================================================================


def _get_period(data):
    """
    Returns the period of the data set. Either day or month.
    """
    max_period_days = pd.to_timedelta(data.time.diff('time', n=1)).max().days

    if max_period_days == 1:
        period = 'dayofyear'
    elif max_period_days >= 28 and max_period_days <= 31:
        period = 'month'
    else:
        raise Exception("Time period not in usual periods")
    return period


def computeMeanClimatology(data):
    """
    Monthly means
    """
    filename = generateFileName(data.name, dataset=data.dataset,
                                processed='meanclim', suffix='nc')
    path = join(processeddir, filename)

    if not exists(path):
        print(f"- Compute {data.name} climatetology")
        period = _get_period(data)
        print(f"- Data has {period} period")

        if reference_period:
            meanclim = data.loc['1981-01-01':'2010-12-31']. \
                groupby(f'time.{period}').mean(dim="time")
        else:
            print("Use the entire time series for the Mean Climatology")
            meanclim = data.groupby(f'time.{period}').mean(dim="time")

        meanclim.to_netcdf(path)
    else:
        print(f"- Read {data.name} climatetology")
        meanclim = xr.open_dataarray(path)
    return meanclim


def computeStdClimatology(data):
    """
    Monthly stds
    """
    filename = generateFileName(data.name, dataset=data.dataset,
                                processed='stdclim', suffix='nc')
    path = join(processeddir, filename)

    if not exists(path):
        print(f"- Compute {data.name} climatetology")
        period = _get_period(data)
        print(f"- Data has {period} period")
        if reference_period:
            stdclim = data.loc['1981-01-01':'2010-12-31']. \
                groupby(f'time.{period}').std(dim="time")
        else:
            print("Use the entire time series for the Std Climatology")
            stdclim = data.groupby(f'time.{period}').std(dim="time")

        stdclim.to_netcdf(path)
    else:
        print(f"- Read {data.name} climatetology")
        stdclim = xr.open_dataarray(path)
    return stdclim


# =============================================================================
# # ===========================================================================
# # Pre-Computation
# # ===========================================================================
# =============================================================================
def computeAnomaly(data):
    """
    Remove the seasonality
    """
    period = _get_period(data)
    meanclim = computeMeanClimatology(data)
    anom = data.groupby(f'time.{period}') - meanclim
    return anom


def computeNormAnomaly(data):
    """
    Remove the seasonality
    """
    period = _get_period(data)
    meanclim = computeMeanClimatology(data)
    stdclim = computeStdClimatology(data)
    normanom = xr.apply_ufunc(lambda x, m, s: (x - m) / s,
                              data.groupby(f'time.{period}'),
                              meanclim, stdclim,
                              dask='allowed')
    return normanom

# =============================================================================
# =============================================================================
# # Attribute manipulation
# =============================================================================
# =============================================================================


def _delete_some_attributes(attrs):
    """
    delete some attributes from the orginal data set that lose meaning after
    data processing

    :param attrs: the attribute list
    """
    to_delete_attrs = ['actual_range', 'valid_range']
    for del_attrs in to_delete_attrs:
        if del_attrs in attrs:
            del attrs[del_attrs]
    return attrs

# =============================================================================
# # ===========================================================================
# # Saving
# # ===========================================================================
# =============================================================================


def toProcessedDir(data, new):
    """
    Save the basic data to the processeddir.
    """
    filename = generateFileName(data.name, dataset=data.dataset, suffix='nc')
    path = join(processeddir, filename)

    if exists(path) and not new:
        print(f"{data.name} already saved in post directory")
    else:
        print(f"save {data.name} in post directory")
        data.to_netcdf(path)

def saveAnomaly(data, new, compute=True):
    """
    save deviation to processeddir
    """
    filename = generateFileName(data.name, dataset=data.dataset,
                                processed='anom', suffix='nc')
    path = join(processeddir, filename)

    if exists(path) and not new:
        print(f"{data.name} anomaly already computed")
    else:
        print(f"Compute {data.name} anomaly")

        if compute:
            print(f"Compute and save {data.name} anomaly")

            anom = computeAnomaly(data)
        else:
            print(f"Save {data.name} anomaly")
            anom = data

        anom.name = ''.join([data.name, 'Anom'])

        anom.attrs = data.attrs.copy()
        anom.attrs['statistic'] = 'Substracted the monthly Mean.'

        anom.attrs = _delete_some_attributes(anom.attrs)

        anom.to_netcdf(path)


def saveNormAnomaly(data, new):
    """
    save deviation to processeddir
    """
    filename = generateFileName(data.name, dataset=data.dataset,
                                processed='normanom', suffix='nc')
    path = join(processeddir, filename)

    if exists(path) and not new:
        print(f"{data.name} normed anomaly already computed")
    else:
        print(f"Compute {data.name} normed anomaly")
        normanom = computeNormAnomaly(data)

        normanom.name = ''.join([data.name, 'NormAnom'])

        normanom.attrs = data.attrs.copy()
        normanom.attrs['statistic'] = 'Substracted the monthly Mean.\
            Divided by the Monthly standard deviation'

        normanom.attrs = _delete_some_attributes(normanom.attrs)
        normanom.to_netcdf(path)


def postprocess(data, new=False, ref_period = True):
    """
    Combine all the postprocessing functions in one data routine.

    :param data: xarray data array
    :param new: compute the statistics again (default = False)
    """
    small_print_header(f"Process {data.name} from {data.dataset}")
    toProcessedDir(data, new)
    #TODO: Do this better!
    global reference_period
    reference_period = ref_period

    saveAnomaly(data, new)
