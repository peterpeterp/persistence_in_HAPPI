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

for hist_file in hist_files:
	print(hist_file)
	orig_dry = da.read_nc(hist_file)['dry']
	orig_wet = da.read_nc(hist_file)['5mm']

	arti_dry = orig_dry.copy()
	arti_wet = orig_wet.copy()

	for y in orig_dry.lat:
		for x in orig_dry.lon:

			if np.sum(dry_orig) > 10 and np.sum(wet_orig) > 10:
				for sea,season_name in {0:'MAM',1:'JJA',2:'SON',3:'DJF'}.items():
					dry_orig_sea = orig_dry[:,y,x].ix[sea_indices[sea]]
					wet_orig_sea = orig_wet[:,y,x].ix[sea_indices[sea]]

					dry_change = int((state_count_fut['dry'][season_name,y,x] - state_count_hist['dry'][season_name,y,x]) /100. )
					wet_change = int((state_count_fut['5mm'][season_name,y,x] - state_count_hist['5mm'][season_name,y,x]) /100. )

					if dry_change > 0 and wet_change > 0:
						# identify candidates
						candidates = np.where((dry_orig_sea!=1) & (wet_orig_sea!=1))[0]
						random_ = random.sample(candidates,wet_change+dry_change)

						# add wet states
						random_wet = random_[:wet_change]
						arti_wet[:,y,x].ix[sea_indices[sea][random_wet]] = 1

						# add wet states
						random_dry = random_[wet_change:]
						arti_dry[:,y,x].ix[sea_indices[sea][random_dry]] = 1

					elif dry_change > 0 and wet_change < 0:
						# remove wet states
						candidates = np.where((wet_orig_sea==1) & (wet_orig_sea!=1))[0]
						random_ = random.sample(candidates,-1*wet_change)
						arti_wet[:,y,x].ix[sea_indices[sea][random_]] = 0

						# add dry states
						candidates = np.where((arti_dry[:,y,x].ix[sea_indices[sea]]!=1) & (dry_orig_sea!=1))[0]
						random_ = random.sample(candidates,dry_change)
						arti_dry[:,y,x].ix[sea_indices[sea][random_]] = 1

					elif dry_change < 0 and wet_change > 0:
						# remove dry states
						candidates = np.where((dry_orig_sea==1) & (wet_orig_sea!=1))[0]
						random_ = random.sample(candidates,-1*dry_change)
						arti_dry[:,y,x].ix[sea_indices[sea][random_]] = 0

						# add wet states
						candidates = np.where((arti_dry[:,y,x].ix[sea_indices[sea]]!=1) & (wet_orig_sea!=1))[0]
						random_ = random.sample(candidates,wet_change)
						arti_wet[:,y,x].ix[sea_indices[sea][random_]] = 1

					elif dry_change < 0 and wet_change < 0:
						# remove wet states
						candidates = np.where((wet_orig_sea==1) & (wet_orig_sea!=1))[0]
						random_ = random.sample(candidates,-1*wet_change)
						arti_wet[:,y,x].ix[sea_indices[sea][random_]] = 0

						# remove dry states
						candidates = np.where((dry_orig_sea==1) & (dry_orig_sea!=1))[0]
						random_ = random.sample(candidates,-1*dry_change)
						arti_dry[:,y,x].ix[sea_indices[sea][random_]] = 0

					elif dry_change > 0 and wet_change == 0:
						# add dry states
						candidates = np.where((dry_orig_sea!=1) & (dry_orig_sea!=1))[0]
						random_ = random.sample(candidates,dry_change)
						arti_dry[:,y,x].ix[sea_indices[sea][random_]] = 1

					elif dry_change < 0 and wet_change == 0:
						# remove dry states
						candidates = np.where((dry_orig_sea==1) & (wet_orig_sea!=1))[0]
						random_ = random.sample(candidates,-1*dry_change)
						arti_dry[:,y,x].ix[sea_indices[sea][random_]] = 0

					elif dry_change == 0 and wet_change > 0:
						# add wet states
						candidates = np.where((dry_orig_sea!=1) & (wet_orig_sea!=1))[0]
						random_ = random.sample(candidates,wet_change)
						arti_wet[:,y,x].ix[sea_indices[sea][random_]] = 1

					elif dry_change == 0 and wet_change < 0:
						# remove wet states
						candidates = np.where((wet_orig_sea==1) & (wet_orig_sea!=1))[0]
						random_ = random.sample(candidates,-1*wet_change)
						arti_wet[:,y,x].ix[sea_indices[sea][random_]] = 0

					elif dry_change == 0 and wet_change == 0:
						pass


					if arti_dry[:,y,x].ix[sea_indices[sea]].sum() - dry_orig_sea.sum() != dry_change:
						asdasd
					if arti_wet[:,y,x].ix[sea_indices[sea]].sum() - wet_orig_sea.sum() != wet_change:
						asdasd


	da.Dataset({'dry':arti_dry,'wet':arti_wet}).write_nc(hist_file.replace('All-Hist',scenario.replace('Future','Artificial-'+str(seed))))








#
