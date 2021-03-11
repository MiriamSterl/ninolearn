"""
This module aims to standardize the training and evaluation procedure.
"""
import numpy as np
import pandas as pd
import xarray as xr

from os.path import join, exists
from os import listdir

from ninolearn.utils import print_header, small_print_header
from ninolearn.pathes import modeldir, processeddir


# evaluation decades
from s0_start import start_pred_y
decades= np.hstack(([1963], np.arange(1972,start_pred_y,10),[start_pred_y])) 
decades_elninolike = []

n_decades = len(decades)
decade_name = np.empty(n_decades-1, dtype=object)
for i in range(n_decades-1):
    decade_name[i] = str(decades[i]) + '-' + str(decades[i+1]-1)



def cross_training(model, pipeline, n_iter, lead_times, **kwargs):
    """
    Training the model on different training sets in which each time a period\
    corresponing to a decade out of 1962-1971, 1972-1981, ..., 2012-last \
    observed date is spared.

    :param model: A model that follows the guidelines how a model object\
    should be set up.

    :param pipeline: a function that takes lead time as argument and returns\
    the corresponding feature, label, time and persistance.

    :param save_dir: The prefix of the save directory.

    :param **kwargs: Arguments that shell be passed to the .set_parameter() \
    method of the provided model.
    """

    for lead_time in lead_times:
        X, y, timey = pipeline(lead_time, return_persistance=False)

        print_header(f'Lead time: {lead_time} months')

        for j in range(n_decades-1):
            m = model(**kwargs)
            dir_name = f"{m.hyperparameters['name']}_decade{decades[j]}_lead{lead_time}"
            path = join(modeldir, dir_name)

            n_files=0
            if exists(path):
                n_files = len(listdir(path))

            if not exists(path) or n_files==0:
                small_print_header(f'Test period: {decades[j]}-01-01 till {decades[j+1]-1}-12-01')

                test_indeces = (timey>=f'{decades[j]}-01-01') & (timey<=f'{decades[j+1]-1}-12-01')
                train_indeces = np.invert(test_indeces)
                trainX, trainy, traintime = X[train_indeces,:], y[train_indeces], timey[train_indeces]

                m.fit_RandomizedSearch(trainX, trainy, traintime, n_iter=n_iter)
                m.save(location=modeldir, dir_name=dir_name)

            else:
                print(f'{dir_name} already exists')
            del m

# def cross_hindcast(model, pipeline, model_name, **kwargs):
#     """
#     Generate a hindcast from 1962 till today using the models which were
#     trained by the .cross_training() method.

#     :param model: The considered model.

#     :param pipeline: The data pipeline that already was used before in \
#     .cross_training().
#     """

#     first_lead_loop = True

#     for i in range(n_lead):
#         lead_time = lead_times[i]
#         print_header(f'Lead time: {lead_time} months')

#         X, y, timey, y_persistance = pipeline(lead_time, return_persistance=True)

#         ytrue = np.array([])
#         timeytrue = pd.DatetimeIndex([])

#         first_dec_loop = True
#         for j in range(n_decades-1):
#             small_print_header(f'Predict: {decades[j]}-01-01 till {decades[j+1]-1}-12-01')

#             # test indices
#             test_indeces = (timey>=f'{decades[j]}-01-01') & (timey<=f'{decades[j+1]-1}-12-01')
#             testX, testy, testtimey = X[test_indeces,:], y[test_indeces], timey[test_indeces]

#             m = model(**kwargs)
#             m.load(location=modeldir, dir_name=f'{model_name}_decade{decades[j]}_lead{lead_time}')

#             # allocate arrays and variables for which the model must be loaded
#             if first_dec_loop:
#                 n_outputs = m.n_outputs

#                 output_names = m.output_names
#                 pred_full = np.zeros((n_outputs, 0))
#                 first_dec_loop=False

#             # make prediction
#             pred = np.zeros((m.n_outputs, testX.shape[0]))
#             pred[:,:] = m.predict(testX)


#             # make the full time series
#             pred_full = np.append(pred_full, pred, axis=1)
#             ytrue = np.append(ytrue, testy)
#             timeytrue = timeytrue.append(testtimey)
#             del m

#         if timeytrue[0]!=pd.to_datetime('1963-01-01'):
#             expected_first_date = '1963-01-01'
#             got_first_date = timeytrue[0].isoformat()[:10]

#             raise Exception(f"The first predicted date for lead time {lead_time} \
#                             is {got_first_date} but expected {expected_first_date}")

#         # allocate arrays and variables for which the full length of the time
#         # series must be known
#         if first_lead_loop:
#             n_time = len(timeytrue)
#             pred_save =  np.zeros((n_outputs, n_time, n_lead))
#             first_lead_loop=False

#         pred_save[:,:,i] =  pred_full

#     # Save data to a netcdf file
#     save_dict = {}
#     for i in range(n_outputs):
#         save_dict[output_names[i]] = (['target_season', 'lead'],  pred_save[i,:,:])

#     ds = xr.Dataset(save_dict, coords={'target_season': timeytrue,
#                                        'lead': lead_times} )
#     ds.to_netcdf(join(processeddir, f'{model_name}_forecasts.nc'))


# def cross_hindcast_dem(model, pipeline, model_name):
#     """
#     Generate a hindcast from 1962 till today using the models which were
#     trained by the .cross_training() method. ONLY works for the DEM.
#     This routine returns an std estimate that is only based on the corrlation
#     skill of the DEM predicted mean.

#     :param model: The considered model.

#     :param pipeline: The data pipeline that already was used before in \
#     .cross_training().
#     """
#     #cross_hindcast(model, pipeline, model_name)

#     std_estimate = xr.open_dataarray(join(processeddir, f'{model_name}_std_estimate.nc'))

#     first_lead_loop = True

#     for i in range(n_lead):
#         lead_time = lead_times[i]
#         print_header(f'Lead time: {lead_time} months')

#         X, y, timey, y_persistance = pipeline(lead_time, return_persistance=True)

#         ytrue = np.array([])
#         timeytrue = pd.DatetimeIndex([])

#         first_dec_loop = True
#         for j in range(n_decades-1):
#             small_print_header(f'Predict: {decades[j]}-01-01 till {decades[j+1]-1}-12-01')

#             # test indices
#             test_indeces = (timey>=f'{decades[j]}-01-01') & (timey<=f'{decades[j+1]-1}-12-01')
#             testX, testy, testtimey = X[test_indeces,:], y[test_indeces], timey[test_indeces]

#             m = model()
#             m.load(location=modeldir, dir_name=f'{model_name}_decade{decades[j]}_lead{lead_time}')

#             # allocate arrays and variables for which the model must be loaded
#             if first_dec_loop:
#                 n_outputs = m.n_outputs
#                 output_names = m.output_names
#                 pred_full = np.zeros((n_outputs+1, 0))
#                 first_dec_loop=False

#             # make prediction
#             pred = np.zeros((m.n_outputs+1, testX.shape[0]))
#             pred[:2,:] = m.predict(testX)

#             for k in range(len(testtimey)):
#                 month = testtimey[k].date().month
#                 pred[-1, k] = std_estimate[i, month-1]

#             # make the full time series
#             pred_full = np.append(pred_full, pred, axis=1)
#             ytrue = np.append(ytrue, testy)
#             timeytrue = timeytrue.append(testtimey)
#             del m

#         if timeytrue[0]!=pd.to_datetime('1963-01-01'):
#             expected_first_date = '1963-01-01'
#             got_first_date = timeytrue[0].isoformat()[:10]

#             raise Exception(f"The first predicted date for lead time {lead_time} \
#                             is {got_first_date} but expected {expected_first_date}")

#         # allocate arrays and variables for which the full length of the time
#         # series must be known
#         if first_lead_loop:
#             n_time = len(timeytrue)
#             pred_save =  np.zeros((n_outputs+1, n_time, n_lead))
#             first_lead_loop=False

#         pred_save[:,:,i] =  pred_full

#     # Save data to a netcdf file
#     save_dict = {}
#     for i in range(n_outputs + 1):
#         if i<n_outputs:
#             save_dict[output_names[i]] = (['target_season', 'lead'],  pred_save[i,:,:])
#         else:
#             save_dict['std_estimate'] = (['target_season', 'lead'],  pred_save[i,:,:])

#     ds = xr.Dataset(save_dict, coords={'target_season': timeytrue,
#                                        'lead': lead_times} )
#     ds.to_netcdf(join(processeddir, f'{model_name}_forecasts_with_std_estimated.nc'))
#     ds.close()