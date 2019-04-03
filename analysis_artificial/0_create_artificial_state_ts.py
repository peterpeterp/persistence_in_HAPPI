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
landmask = da.read_nc('masks/landmask_'+model_dict[model]['grid']+'.nc')['landmask']

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
	sea_indices[sea] = np.array([],np.int)
	for i in range(100):
		sea_indices[sea] = np.append(sea_indices[sea],np.where(season==sea)[0] + i*season.shape[0])

nc = Dataset(hist_files[0])
lat = nc.variables['lat'][:]
lat_nh = lat[lat>0]
for file_name in hist_files:
	dataset = Dataset(file_name.replace('All-Hist',scenario.replace('Future','Artificial-'+str(seed))), 'w', format='NETCDF4_CLASSIC')
	lat_d = dataset.createDimension('lat', len(lat))
	lon_d = dataset.createDimension('lon', None)
	time_d = dataset.createDimension('time', nc.dimensions['time'].size)

	time_v = dataset.createVariable('time', np.float64, ('time',)); time_v[:] = nc.variables['time'][:]
	lat_v = dataset.createVariable('lat', np.float32,('lat',)); lat_v[:] = lat
	lon_v = dataset.createVariable('lon', np.float32,('lon',))

	for key in ['dry','5mm']:
		globals()[key] = dataset.createVariable(key, np.int8,('time','lat','lon'))

	dataset.close()




lat_nh = lat[lat>0]
lat_i = np.where(lat>0)[0]
for yi,y in zip(lat_i,lat_nh):
	hist_merge = {}
	nc = Dataset(hist_files[0])
	hist_merge['dry'] = nc['dry'][:,yi,:]
	hist_merge['5mm'] = nc['5mm'][:,yi,:]
	hist_merge['run_id'] = np.zeros([3650]) * 0

	for i_run,file_name in enumerate(hist_files[1:]):
		print(file_name)
		nc = Dataset(file_name)
		hist_merge['dry'] = np.concatenate((hist_merge['dry'], nc['dry'][:,yi,:]))
		hist_merge['5mm'] = np.concatenate((hist_merge['5mm'], nc['5mm'][:,yi,:]))
		hist_merge['run_id'] = np.concatenate((hist_merge['run_id'], np.zeros([3650]) + i_run+1))

	for xi,x in enumerate(nc.variables['lon'][:]):
		print(xi)
		orig_dry = hist_merge['dry'][:,xi].copy()
		orig_wet = hist_merge['5mm'][:,xi].copy()

		arti_dry = hist_merge['dry'][:,xi].copy()
		arti_wet = hist_merge['5mm'][:,xi].copy()

		if orig_dry.sum()>100 and orig_wet.sum()>100:

			for sea,season_name in {0:'MAM',1:'JJA',2:'SON',3:'DJF'}.items():

				dry_change = int(state_count_fut['dry'][season_name,y,x] - state_count_hist['dry'][season_name,y,x])
				wet_change = int(state_count_fut['5mm'][season_name,y,x] - state_count_hist['5mm'][season_name,y,x])


				if dry_change > 0 and wet_change > 0:
					# identify candidates
					candidates = np.where((orig_dry[sea_indices[sea]]!=1) & (orig_wet[sea_indices[sea]]!=1))[0]
					random_ = np.array(random.sample(candidates,wet_change+dry_change))

					# add wet states
					random_wet = random_[:wet_change]
					arti_wet[sea_indices[sea][random_wet]] = 1

					# add wet states
					random_dry = random_[wet_change:]
					arti_dry[sea_indices[sea][random_dry]] = 1

				elif dry_change > 0 and wet_change < 0:
					# remove wet states
					candidates = np.where(orig_wet[sea_indices[sea]]==1)[0]
					random_ = np.array(random.sample(candidates,-1*wet_change))
					arti_wet[sea_indices[sea][random_]] = 0

					# add dry states
					candidates = np.where((arti_dry[sea_indices[sea]]!=1) & (orig_dry[sea_indices[sea]]!=1))[0]
					random_ = np.array(random.sample(candidates,dry_change))
					arti_dry[sea_indices[sea][random_]] = 1

				elif dry_change < 0 and wet_change > 0:
					# remove dry states
					candidates = np.where(orig_dry[sea_indices[sea]]==1)[0]
					random_ = np.array(random.sample(candidates,-1*dry_change))
					arti_dry[sea_indices[sea][random_]] = 0

					# add wet states
					candidates = np.where((arti_dry[sea_indices[sea]]!=1) & (orig_wet[sea_indices[sea]]!=1))[0]
					random_ = np.array(random.sample(candidates,wet_change))
					arti_wet[sea_indices[sea][random_]] = 1

				elif dry_change < 0 and wet_change < 0:
					# remove wet states
					candidates = np.where(orig_wet[sea_indices[sea]]==1)[0]
					random_ = np.array(random.sample(candidates,-1*wet_change))
					arti_wet[sea_indices[sea][random_]] = 0

					# remove dry states
					candidates = np.where(orig_dry[sea_indices[sea]]==1)[0]
					random_ = np.array(random.sample(candidates,-1*dry_change))
					arti_dry[sea_indices[sea][random_]] = 0

				elif dry_change > 0 and wet_change == 0:
					# add dry states
					candidates = np.where((orig_dry[sea_indices[sea]]!=1) & (orig_dry[sea_indices[sea]]!=1))[0]
					random_ = np.array(random.sample(candidates,dry_change))
					arti_dry[sea_indices[sea][random_]] = 1

				elif dry_change < 0 and wet_change == 0:
					# remove dry states
					candidates = np.where(orig_dry[sea_indices[sea]]==1)[0]
					random_ = np.array(random.sample(candidates,-1*dry_change))
					arti_dry[sea_indices[sea][random_]] = 0

				elif dry_change == 0 and wet_change > 0:
					# add wet states
					candidates = np.where((orig_dry[sea_indices[sea]]!=1) & (orig_wet[sea_indices[sea]]!=1))[0]
					random_ = np.array(random.sample(candidates,wet_change))
					arti_wet[sea_indices[sea][random_]] = 1

				elif dry_change == 0 and wet_change < 0:
					# remove wet states
					candidates = np.where(orig_wet[sea_indices[sea]]==1)[0]
					random_ = np.array(random.sample(candidates,-1*wet_change))
					arti_wet[sea_indices[sea][random_]] = 0

				elif dry_change == 0 and wet_change == 0:
					pass


				if np.sum(arti_dry[sea_indices[sea]]==1) - np.sum(orig_dry[sea_indices[sea]]==1) != dry_change:
					asdasd
				if np.sum(arti_wet[sea_indices[sea]]==1) - np.sum(orig_wet[sea_indices[sea]]==1) != wet_change:
					asdasd

				gc.collect()


		for i_run,file_name in enumerate(hist_files):
			dataset = Dataset(file_name.replace('All-Hist',scenario.replace('Future','Artificial-'+str(seed))), 'a', format='NETCDF4_CLASSIC')

			dataset.variables['dry'][:,yi,xi] = arti_dry[hist_merge['run_id'] == i_run]
			dataset.variables['5mm'][:,yi,xi] = arti_wet[hist_merge['run_id'] == i_run]
			dataset.variables['lon'][xi] = x
			dataset.close()



#
