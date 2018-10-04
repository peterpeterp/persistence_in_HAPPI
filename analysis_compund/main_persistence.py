import os,sys,glob,time,collections,signal
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
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

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
from persistence_functions import *

try:
	os.chdir('/global/homes/p/pepflei/')
	model=sys.argv[1]
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
	chosen_scenario=sys.argv[2]
	print model
except:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
	model='CAM4-2degree'
	working_path='data/'+model+'/'
	chosen_scenario='All-Hist'

sys.path.append('persistence_in_models/')
import __settings
model_dict=__settings.model_dict


in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

try:
	os.chdir('/global/homes/p/pepflei/')
	land_mask_file='/global/homes/p/pepflei/masks/landmask_'+grid+'_NA-1.nc'
except:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
	land_mask_file='data/'+model+'/landmask_'+grid+'_NA-1.nc'


for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2115','2106/2115','2006/2015']):
	if scenario==chosen_scenario:
		os.system('mkdir '+working_path+scenario)
		run_list=sorted([path.split('/')[-1].split('_')[-1].split('.')[0] for path in glob.glob('/global/cscratch1/sd/pepflei/EKE/'+model+'/All-Hist/monEKE*')])[0:100]
		for run in run_list:
			print(run)
			start_time=time.time()

			###############
			# Temperature
			###############

			tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/tas/'
			raw_file=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			tas_state_file=raw_file.replace('.nc','_state.nc')
			if os.path.isfile(tas_state_file) == False:
				# get daily temp
				out_file_name_tmp=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'_tmp.nc'
				command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name_tmp
				result=try_several_times(command,2,60)
				result=try_several_times('cdo -O -selyear,'+selyears+' '+out_file_name_tmp+' '+raw_file,2,60)
				result=try_several_times('rm '+out_file_name_tmp)

				# mask ocean
				land_file=raw_file.replace('.nc','_land.nc')
				result=try_several_times('cdo -O mul '+raw_file+' '+land_mask_file+' '+land_file)

				# detrend
				a=raw_file.replace('.nc','_a.nc')
				b=raw_file.replace('.nc','_b.nc')
				result=try_several_times('cdo -O trend '+land_file+' '+a+' '+b)
				detrend_1=raw_file.replace('.nc','_detrend_1.nc')
				result=try_several_times('cdo -O subtrend '+land_file+' '+a+' '+b+' '+detrend_1,1,120)

				runmean=raw_file.replace('.nc','_runmean.nc')
				result=try_several_times('cdo -O runmean,90 '+detrend_1+' '+runmean,1,120)

				detrend_cut=raw_file.replace('.nc','_detrend_cut.nc')
				command='cdo -O delete,timestep='
				for i in range(1,46,1): command+=str(i)+','
				for i in range(1,46,1): command+=str(-i)+','
				result=try_several_times(command+' '+detrend_1+' '+detrend_cut)
				anom_file=raw_file.replace('.nc','_anom.nc')
				result=try_several_times('cdo -O sub '+detrend_cut+' '+runmean+' '+anom_file,1,120)

				# # state
				temp_anomaly_to_ind(anom_file,tas_state_file,overwrite=True)

				# clean
				os.system('rm '+raw_file+' '+land_file+' '+a+' '+b+' '+detrend_1+' '+runmean+' '+detrend_cut)


			###############
			# Precipitation
			###############

			tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/pr/'
			raw_file=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			pr_state_file=raw_file.replace('.nc','_state.nc')
			if os.path.isfile(pr_state_file) == False:

				# get daily pr
				out_file_name_tmp=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'_tmp.nc'
				command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name_tmp
				result=try_several_times(command,2,60)
				result=try_several_times('cdo -O -selyear,'+selyears+' '+out_file_name_tmp+' '+raw_file,2,60)
				result=try_several_times('rm '+out_file_name_tmp)

				# mask ocean
				land_file=raw_file.replace('.nc','_land.nc')
				result=try_several_times('cdo -O mul '+raw_file+' '+land_mask_file+' '+land_file)

				# # state
				if scenario == 'All-Hist':
					precip_to_index(land_file,pr_state_file,overwrite=True,unit_multiplier=86400,threshold=1)

				else:
					pr_percentile_file = glob.glob(working_path+'All-Hist'+'/pr_*_'+run+'_percentile1mm.nc')
					if os.path.isfile(pr_percentile_file) is False:
						pr_hist_state_file = glob.glob(working_path+'All-Hist'+'/pr_*_'+run+'_state.nc')
						result=try_several_times('cdo chname,pr,qu -divc,36.5 -timsum -setrtoc,-10,0,0 ' + pr_hist_state_file + ' ' + pr_percentile_file)

					precip_to_index_percentile(land_file,pr_state_file,pr_percentile_file,overwrite=True,threshold=1)

				# clean
				os.system('rm '+land_file)

			###############
			# Compound
			###############
			compound_state_file=tas_state_file.replace('tas_Aday','compound_Aday')
			if os.path.isfile(compound_state_file) == False:
				compound_precip_temp_index(tas_state_file,pr_state_file,compound_state_file)

			gc.collect()

			###############
			# Compound
			###############

			compound_period_file=compound_state_file.replace('_state.nc','_period.nc')
			print(compound_period_file)
			if os.path.isfile(compound_period_file) == False:
				get_persistence(compound_state_file,compound_period_file,overwrite=True)
			gc.collect()
			pr_period_file=pr_state_file.replace('_state.nc','_period.nc')
			print(pr_period_file)
			if os.path.isfile(pr_period_file) == False:
				get_persistence(pr_state_file,pr_period_file,overwrite=True)
			gc.collect()
			tas_period_file=tas_state_file.replace('_state.nc','_period.nc')
			print(tas_period_file)
			if os.path.isfile(tas_period_file) == False:
				get_persistence(tas_state_file,tas_period_file,overwrite=True)
			gc.collect()
