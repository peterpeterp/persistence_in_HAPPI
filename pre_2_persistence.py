import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
from persistence_functions import *

model_dict={'MIROC':{'grid':'128x256','path':'/global/cscratch1/sd/pepflei/MIROC/MIROC5/'},
			'NorESM1':{'grid':'192x288','path':'/global/cscratch1/sd/pepflei/NCC/NorESM1-HAPPI/'},
			'ECHAM6-3-LR':{'grid':'96x192','path':'/global/cscratch1/sd/pepflei/MPI-M/ECHAM6-3-LR/'},
			'CAM4-2degree':{'grid':'96x144','path':'/global/cscratch1/sd/pepflei/ETH/CAM4-2degree/'},
}

model=sys.argv[1]
print model

overwrite=False

working_path=model_dict[model]['path']
grid=model_dict[model]['grid']

for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
	run_count=0
	all_files=[raw for raw in glob.glob(working_path+scenario+'/*') if len(raw.split('/')[-1].split('_'))==7]
	for in_file in all_files:
		print in_file
		test=da.read_nc(in_file)
		if len(test.time/365.)>9.:
			if in_file.split('_')[-1]!='period.nc' and run_count<100:
				print in_file
				if os.path.isfile(in_file.replace('.nc','_period.nc')) and overwrite: os.system('rm '+in_file.replace('.nc','_period.nc'))
				if os.path.isfile(in_file.replace('.nc','_period.nc'))==False:
					start_time=time.time()

					try:
						# mask ocean
						land_file=in_file.replace('.nc','_land.nc')
						os.system('cdo -O mul '+in_file+' /global/homes/p/pepflei/masks/landmask_'+grid+'_NA-1.nc '+land_file)

						# detrend
						a=in_file.replace('.nc','_a.nc')
						b=in_file.replace('.nc','_b.nc')
						os.system('cdo -O trend '+land_file+' '+a+' '+b)
						detrend_1=in_file.replace('.nc','_detrend_1.nc')
						os.system('cdo -O subtrend '+land_file+' '+a+' '+b+' '+detrend_1)

						runmean=in_file.replace('.nc','_runmean.nc')
						os.system('cdo -O runmean,90 '+detrend_1+' '+runmean)

						detrend_cut=in_file.replace('.nc','_detrend_cut.nc')
						command='cdo -O delete,timestep='
						for i in range(1,46,1): command+=str(i)+','
						for i in range(1,46,1): command+=str(-i)+','
						os.system(command+' '+detrend_1+' '+detrend_cut)
						anom_file=in_file.replace('.nc','_anom.nc')
						print 'anom',anom_file
						os.system('cdo -O sub '+detrend_cut+' '+runmean+' '+anom_file)

						# state
						state_file=in_file.replace('.nc','_state.nc')
						print 'state',state_file
						temp_anomaly_to_ind(anom_file,state_file,overwrite=True)

						# persistence
						print state_file,in_file.replace('.nc','_period.nc')
						get_persistence(state_file,in_file.replace('.nc','_period.nc'),overwrite=True)
						print 'processing time:',time.time()-start_time

						run_count+=1

					except:
						failed_files=open('out/persistence_fails'+model+'.txt','w')
						failed_files.write(state_file+'\n')
						failed_files.close()
						print '/!\---------------/!\ \n failed for',state_file,'\n/!\---------------/!\ '

					# clean
					os.system('rm '+land_file+' '+a+' '+b+' '+detrend_1+' '+runmean+' '+detrend_cut+' '+anom_file+' '+state_file)
