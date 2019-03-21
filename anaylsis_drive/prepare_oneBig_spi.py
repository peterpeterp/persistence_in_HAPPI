import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
import subprocess as sub


try:
	model=sys.argv[1]
	print model,scenario

except:
	model = 'CAM4-2degree'

try:
	sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
	os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')
	working_path='/p/tmp/pepflei/HAPPI/raw_data/SPI/'+model+'/'
	home_path = '/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/'
except:
	sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/SPI/'+model+'/'
	home_path = '/global/homes/p/pepflei/persistence_in_models/'



import __settings
model_dict=__settings.model_dict
masks = da.read_nc('masks/srex_mask_'+model_dict[model]['grid']+'.nc')


for scenario in scenarios:
	all_files=sorted(glob.glob(working_path+scenario+'/SPI*_'+scenario+'*.nc'))

	big_merge = {}
	big_merge['SPI'] = da.read_nc(all_files[0])['SPI'][:,0:,:]
	big_merge['run_id'] = da.read_nc(all_files[0])['SPI'][:,0:,:].copy()
	big_merge['run_id'].values = 0

	for i_run,file_name in enumerate(all_files[1:]):
		print(file_name)
		big_merge['SPI'] = da.concatenate((big_merge['SPI'], da.read_nc(file_name)['SPI'][:,0:,:]))
		big_merge['run_id'] = da.read_nc(file_name)['SPI'][:,0:,:].copy()
		big_merge['run_id'].values = i_run+1

	for region in ['EAS','TIB','CAS','WAS','MED','CEU','ENA','CNA','WNA','NAS','NEU','CGI','ALA']:
		mask = masks[region][0:,:]
		lats = np.where(np.nanmax(mask,axis=1)!=0)[0]
		lons = np.where(np.nanmax(mask,axis=0)!=0)[0]

		da.Dataset({key:val.ix[:,lats,lons] for key,val in big_merge.items()}).write_nc(working_path+scenario+'/'+'_'.join(['SPI',model,scenario,'bigMerge',region])+'.nc')

	da.Dataset({key:val.ix[:,35:60,:] for key,val in big_merge.items()}).write_nc(working_path+scenario+'/'+'_'.join(['SPI',model,scenario,'bigMerge','NHml'])+'.nc')

	del big_merge
	gc.collect()


	'''
	for model in NorESM1 MIROC5 ECHAM6-3-LR CAM4-2degree; do sbatch job_Rscript.sh /p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/analysis_spi/SPI.r /p/tmp/pepflei/HAPPI/raw_data/SPI_stuff/${model}/pr_big_merge.nc pr 3 -13200 -13200 -1 /p/tmp/pepflei/HAPPI/raw_data/SPI_stuff/${model}/pr_big_merge_SPI3.nc; done;
	'''
