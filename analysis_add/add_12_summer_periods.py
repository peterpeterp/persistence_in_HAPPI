import os,sys,glob,time,collections,gc,itertools,timeit,signal

import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
import random as random
import subprocess as sub

def wait_timeout(proc, seconds):
	"""Wait for a process to finish, or raise exception after timeout"""
	start = time.time()
	end = start + seconds
	interval = min(seconds / 1000.0, .25)

	while True:
		result = proc.poll()
		if result is not None:
			return result
		if time.time() >= end:
			os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
			return 'failed'
		time.sleep(interval)


def try_several_times(command,trials=2,seconds=60):
	for trial in range(trials):
		proc=sub.Popen(command,stdout=sub.PIPE,shell=True, preexec_fn=os.setsid)
		result=wait_timeout(proc,seconds)
		if result!='failed':
			break
	return(result)


sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Projects/Persistence/weather_persistence/')
from summer_persistence_analysis import *
from persistence_functions import *

try:
	model=sys.argv[1]
	print model
except:
	model='ECHAM6-3-LR'

overwrite=True

try:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
except:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
	working_path='data/'+model+'/'

sys.path.append('persistence_in_models/')
import __settings
model_dict=__settings.model_dict

in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2115','2106/2115','2006/2015']):

	all_files=glob.glob(working_path+scenario+'/summerStat/tas_Aday_*_summer.nc')

	example_file=da.read_nc(all_files[0])

	merged_=da.Dataset({
		'hottest_day':da.DimArray(axes=[range(100),['7','14','21','28'],example_file.lat,example_file.lon],dims=['run','length','lat','lon']),
		'mean_temp':da.DimArray(axes=[range(100),['7','14','21','28'],example_file.lat,example_file.lon],dims=['run','length','lat','lon']),
		'hottest_day_shift':da.DimArray(axes=[range(100),['7','14','21','28'],example_file.lat,example_file.lon],dims=['run','length','lat','lon']),
	})

	for id,in_file in enumerate(all_files):
		print(id)
		tmp = da.read_nc(in_file)

		for var in ['hottest_day','hottest_day_shift','mean_temp']:
			merged_[var][id,:,:,:] = tmp[var]

	out_file=da.Dataset({
		'length' : da.DimArray(['7','14','21','28'],axes=[['7','14','21','28']],dims=['length']),
		'lon': example_file['lon'],
		'lat': example_file['lat'],
	})

	for var in ['hottest_day','hottest_day_shift','mean_temp']:
		out_file[var] = da.DimArray(np.nanmean(merged_[var],axis=0),axes=[['7','14','21','28'],example_file.lat,example_file.lon],dims=['length','lat','lon'])

	out_file.write_nc('data/'+model+'/tas_'+model+'_'+scenario+'_summerStat.nc','w')
#
