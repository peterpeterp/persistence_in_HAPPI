import os,sys,glob,time,collections,gc,random
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
import subprocess as sub


try:
	model=sys.argv[1]
	scenario=sys.argv[2]
	seed=sys.argv[3]
	print model,scenario

except:
	model = 'CAM4-2degree'
	scenario = 'Plus20-Future'
	seed = 1

try:
	sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
	os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')
	in_path='/p/tmp/pepflei/HAPPI/raw_data/'+model+'/'
	out_path='/p/tmp/pepflei/HAPPI/raw_data/reg_merge/'+model+'/'
	home_path = '/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/'

except:
	sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
	os.chdir('/global/homes/p/pepflei/')


os.system('mkdir -p '+in_path+scenario.replace('Future','Artificial-'+str(seed))+'/pr/')

import __settings
model_dict=__settings.model_dict

state_count_fut = da.read_nc('/p/projects/ikiimp/HAPPI/HAPPI_Peter/data/'+model+'/state_stats/pr_*'+scenario+'*')
state_count_hist = da.read_nc('/p/projects/ikiimp/HAPPI/HAPPI_Peter/data/'+model+'/state_stats/pr_*All-Hist*')

hist_files=sorted(glob.glob(in_path+'All-Hist/pr/*_All-Hist*state.nc'))

# get seasonal indices
seasons={'MAM':{'months':[3,4,5],'index':0}, 'JJA':{'months':[6,7,8],'index':1}, 'SON':{'months':[9,10,11],'index':2}, 'DJF':{'months':[12,1,2],'index':3}}
nc_in=da.read_nc(hist_files[0])
if 'calendar' in nc_in['time'].attrs.keys():
	datevar = num2date(nc_in['time'].values,units = nc_in['time'].units,calendar = nc_in['time'].calendar)
else:
	datevar = num2date(nc_in['time'].values,units = nc_in['time'].units)
month=np.array([int(str(date).split("-")[1])	for date in datevar[:]])
season=month.copy()*np.nan
for sea in seasons.keys():
	season[np.where((month==seasons[sea]['months'][0]) | (month==seasons[sea]['months'][1]) | (month==seasons[sea]['months'][2]) )[0]]=seasons[sea]['index']
sea_indices = {}
for sea in range(4):
	sea_indices[sea] = np.where(season==sea)[0]

nc = Dataset(hist_files[0])
lat = nc.variables['lat'][:]
lat_nh = lat[lat>0]
for file_name in hist_files:
	dataset = Dataset(file_name.replace('All-Hist',scenario.replace('Future','Artificial-'+str(seed))), 'w', format='NETCDF4_CLASSIC')
	lat_d = dataset.createDimension('lat', len(lat_nh))
	lon_d = dataset.createDimension('lon', None)
	time_d = dataset.createDimension('time', nc.dimensions['time'].size)

	time_v = dataset.createVariable('time', np.float64, ('time',)); time_v[:] = nc.variables['time'][:]
	lat_v = dataset.createVariable('lat', np.float32,('lat',)); lat_v[:] = lat_nh
	lon_v = dataset.createVariable('lon', np.float32,('lon',))

	for key in ['dry','wet']:
		globals()[key] = dataset.createVariable(key, np.int8,('time','lat','lon'))

	dataset.close()





for yi,y in enumerate(lat_nh):
	big_merge = {}
	nc = Dataset(hist_files[0])
	for key in ['dry','wet']:
		big_merge[key] = nc[key][:,yi,:]
	big_merge['run_id'] = nc[key][:,yi,:].copy()
	big_merge['run_id'][:] = 0


	for i_run,file_name in enumerate(hist_files[1:]):
		print(file_name)
		nc = Dataset(file_name)
		for key in ['dry','wet']:
			big_merge[key] = np.concatenate((big_merge[key], nc[key][:,yi,:]))
		tmp = nc[key][:,yi,:].copy()
		tmp[:] = i_run+1
		big_merge['run_id'] = np.concatenate((big_merge['run_id'], tmp))

	for xi,x in enumerate(nc.variables['lon'][:]):
		print(xi)
		orig_dry = big_merge['dry'][:,xi]
		orig_wet = big_merge['wet'][:,xi]

		arti_dry = orig_dry.copy()
		arti_wet = orig_wet.copy()

		if np.sum(orig_dry) > 10 and np.sum(orig_wet) > 10:
			for sea,season_name in {0:'MAM',1:'JJA',2:'SON',3:'DJF'}.items():
				dry_orig_sea = orig_dry[sea_indices[sea]]
				wet_orig_sea = orig_wet[sea_indices[sea]]

				dry_change = int(state_count_fut['dry'][season_name,y,x] - state_count_hist['dry'][season_name,y,x])
				wet_change = int(state_count_fut['5mm'][season_name,y,x] - state_count_hist['5mm'][season_name,y,x])

				if dry_change > 0 and wet_change > 0:
					# identify candidates
					candidates = np.where((dry_orig_sea!=1) & (wet_orig_sea!=1))[0]
					random_ = random.sample(candidates,wet_change+dry_change)

					# add wet states
					random_wet = random_[:wet_change]
					arti_wet[sea_indices[sea][random_wet]] = 1

					# add wet states
					random_dry = random_[wet_change:]
					arti_dry[sea_indices[sea][random_dry]] = 1

				elif dry_change > 0 and wet_change < 0:
					# remove wet states
					candidates = np.where((wet_orig_sea==1) & (wet_orig_sea!=1))[0]
					random_ = random.sample(candidates,-1*wet_change)
					arti_wet[sea_indices[sea][random_]] = 0

					# add dry states
					candidates = np.where((arti_dry[sea_indices[sea]]!=1) & (dry_orig_sea!=1))[0]
					random_ = random.sample(candidates,dry_change)
					arti_dry[sea_indices[sea][random_]] = 1

				elif dry_change < 0 and wet_change > 0:
					# remove dry states
					candidates = np.where((dry_orig_sea==1) & (wet_orig_sea!=1))[0]
					random_ = random.sample(candidates,-1*dry_change)
					arti_dry[sea_indices[sea][random_]] = 0

					# add wet states
					candidates = np.where((arti_dry[sea_indices[sea]]!=1) & (wet_orig_sea!=1))[0]
					random_ = random.sample(candidates,wet_change)
					arti_wet[sea_indices[sea][random_]] = 1

				elif dry_change < 0 and wet_change < 0:
					# remove wet states
					candidates = np.where((wet_orig_sea==1) & (wet_orig_sea!=1))[0]
					random_ = random.sample(candidates,-1*wet_change)
					arti_wet[sea_indices[sea][random_]] = 0

					# remove dry states
					candidates = np.where((dry_orig_sea==1) & (dry_orig_sea!=1))[0]
					random_ = random.sample(candidates,-1*dry_change)
					arti_dry[sea_indices[sea][random_]] = 0

				elif dry_change > 0 and wet_change == 0:
					# add dry states
					candidates = np.where((dry_orig_sea!=1) & (dry_orig_sea!=1))[0]
					random_ = random.sample(candidates,dry_change)
					arti_dry[sea_indices[sea][random_]] = 1

				elif dry_change < 0 and wet_change == 0:
					# remove dry states
					candidates = np.where((dry_orig_sea==1) & (wet_orig_sea!=1))[0]
					random_ = random.sample(candidates,-1*dry_change)
					arti_dry[sea_indices[sea][random_]] = 0

				elif dry_change == 0 and wet_change > 0:
					# add wet states
					candidates = np.where((dry_orig_sea!=1) & (wet_orig_sea!=1))[0]
					random_ = random.sample(candidates,wet_change)
					arti_wet[sea_indices[sea][random_]] = 1

				elif dry_change == 0 and wet_change < 0:
					# remove wet states
					candidates = np.where((wet_orig_sea==1) & (wet_orig_sea!=1))[0]
					random_ = random.sample(candidates,-1*wet_change)
					arti_wet[sea_indices[sea][random_]] = 0

				elif dry_change == 0 and wet_change == 0:
					pass


				if arti_dry[sea_indices[sea]].sum() - dry_orig_sea.sum() != dry_change:
					asdasd
				if arti_wet[sea_indices[sea]].sum() - wet_orig_sea.sum() != wet_change:
					asdasd

				gc.collect()

		for i_run,file_name in enumerate(hist_files):
			dataset = Dataset(file_name.replace('All-Hist',scenario.replace('Future','Artificial-'+str(seed))), 'a', format='NETCDF4_CLASSIC')

			dataset.variables['dry'][:,yi,xi] = arti_dry[big_merge['run_id'][:,0] == i_run]
			dataset.variables['wet'][:,yi,xi] = arti_wet[big_merge['run_id'][:,0] == i_run]
			dataset.variables['lon'][xi] = x
			dataset.close()



#
