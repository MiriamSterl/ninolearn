from ninolearn.preprocess.pca import pca
from ninolearn.IO.read_processed import data_reader

# =============================================================================
# decadal PCAs
# =============================================================================

reader = data_reader(startdate='1955-01', enddate='2018-12',lon_min=120, lon_max=300)
sst = reader.read_netcdf('sst', dataset='ERSSTv5', processed='anom')

#%%
sst_decadal = sst.rolling(time=60, center=False).mean()
sst_decadal.attrs = sst.attrs.copy()
sst_decadal.name = f'dec_{sst.name}'

pca_sst_decadal = pca(n_components=6)

pca_sst_decadal.set_eof_array(sst_decadal)
pca_sst_decadal.compute_pca()
pca_sst_decadal.save(extension='.csv', filename='dec_sst_ERSSTv5_anom')
