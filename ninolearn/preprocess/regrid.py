#from ninolearn.IO import read_raw

import xarray as xr
import numpy as np
import iris
import iris.analysis
from iris.coords import DimCoord
from iris.cube import Cube


def to2_5x2_5(data):
    """
    Regrids data the 2.5x2.5 from the NCEP reanalysis data set.

    :param data: An xarray DataArray.
    """
    data_iris = data.to_iris()
    latitude = DimCoord(np.arange(-90, 90.01, 2.5),
                     standard_name='latitude',
                     units='degrees')
    longitude = DimCoord(np.arange(0, 359.99, 2.5),
                      standard_name='longitude',
                      units='degrees')
    cube = Cube(np.zeros((73, 144), np.float32),
             dim_coords_and_dims=[(latitude, 0),
                                 (longitude, 1)])
    scheme = iris.analysis.Linear(extrapolation_mode='extrapolate')
    data_new = data_iris.regrid(cube,scheme)
    data_regridded = xr.DataArray.from_iris(data_new)
    return data_regridded