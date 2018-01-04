import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

model=sys.argv[1]
print model

overwrite=True

try:
    os.chdir('/global/homes/p/pepflei/')
    working_path='/global/cscratch1/sd/pepflei/'+model+'/'
except:
    os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
    working_path='/Users/peterpfleiderer/Documents/Projects/Persistence/data/'+model+'/'

period_number_limit=100

for scenario in ['All-Hist','Plus20-Future','Plus15-Future']:
    out_file=working_path+'/'+model+'_'+scenario+'_summerQ90.nc'
    if overwrite and os.path.isfile(out_file):	os.system('rm '+out_file)
    if os.path.isfile(out_file)==False:
        all_files=glob.glob(working_path+scenario+'/*summer*')
        runs=[str(ff.split('_')[-2].split('.')[0]) for ff in all_files]

        ds=da.Dataset({
            'x90_cum_temp':da.DimArray(axes=[np.asarray(runs),np.asarray(range(period_number_limit),np.int32),qu_90.lat,qu_90.lon],dims=['run','ID','lat','lon']),
            'x90_mean_temp':da.DimArray(axes=[np.asarray(runs),np.asarray(range(period_number_limit),np.int32),qu_90.lat,qu_90.lon],dims=['run','ID','lat','lon']),
            'x90_hottest_day_shift':da.DimArray(axes=[np.asarray(runs),np.asarray(range(period_number_limit),np.int32),qu_90.lat,qu_90.lon],dims=['run','ID','lat','lon']),
            'x90_hottest_day':da.DimArray(axes=[np.asarray(runs),np.asarray(range(period_number_limit),np.int32),qu_90.lat,qu_90.lon],dims=['run','ID','lat','lon']),
            'original_period_id':da.DimArray(axes=[np.asarray(runs),np.asarray(range(period_number_limit),np.int32),qu_90.lat,qu_90.lon],dims=['run','ID','lat','lon']),
            'TXx_in_x90':da.DimArray(axes=[np.asarray(runs),np.arange(0,10,1),qu_90.lat,qu_90.lon],dims=['run','year','lat','lon'])
        })

        print all_files
        for summer_file in all_files:
            start_time=time.time()
            run=str(summer_file.split('_')[-2].split('.')[0])
            print summer_file,run
            summer=da.read_nc(summer_file)

            for var in ds.keys():
                ds[var][run,summer.ID,:,:]=summer[var]

        ds.write_nc(out_file, mode='w')
