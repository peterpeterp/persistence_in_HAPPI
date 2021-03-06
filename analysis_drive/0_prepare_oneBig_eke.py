import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
import subprocess as sub


try:
	model=sys.argv[1]
	scenario=sys.argv[2]
	print model,scenario

except:
	model = 'NorESM1'
	scenario = 'All-Hist'

try:
	sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
	os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')
	in_path='/p/tmp/pepflei/HAPPI/raw_data/EKE/'+model+'/'
	out_path='/p/tmp/pepflei/HAPPI/raw_data/reg_merge/'+model+'/'
	home_path = '/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/'
except:
	sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/EKE/'+model+'/'
	working_path='/global/cscratch1/sd/pepflei/EKE/'+model+'/'
	home_path = '/global/homes/p/pepflei/persistence_in_models/'



import __settings
model_dict=__settings.model_dict
masks = da.read_nc('masks/srex_mask_'+model_dict[model]['grid']+'.nc')


all_files=sorted(glob.glob(in_path+scenario+'/monEKE*_'+scenario+'*.nc'))

big_merge = {}
big_merge['eke'] = da.read_nc(all_files[0])['eke'][:,0:,:]
big_merge['run_id'] = da.read_nc(all_files[0])['eke'][:,0:,:].copy()
big_merge['run_id'].values = 0

for i_run,file_name in enumerate(all_files[1:]):
	print(file_name)
	big_merge['eke'] = da.concatenate((big_merge['eke'], da.read_nc(file_name)['eke'][:,0:,:]))
	tmp = da.read_nc(file_name)['eke'][:,0:,:].copy()
	tmp.values = i_run+1
	big_merge['run_id'] = da.concatenate((big_merge['run_id'], tmp))

for region in ['EAS','TIB','CAS','WAS','MED','CEU','ENA','CNA','WNA','NAS','NEU','CGI','ALA']:
	mask = masks[region][0:,:]
	lats = np.where(np.nanmax(mask,axis=1)!=0)[0]
	lons = np.where(np.nanmax(mask,axis=0)!=0)[0]

	da.Dataset({key:val.ix[:,lats,lons] for key,val in big_merge.items()}).write_nc(out_path+'_'.join(['EKE',model,scenario,'bigMerge',region])+'.nc')

da.Dataset({key:val[:,35:60,:] for key,val in big_merge.items()}).write_nc(out_path+'_'.join(['EKE',model,scenario,'bigMerge','NHml'])+'.nc')









# del big_merge
# gc.collect()
