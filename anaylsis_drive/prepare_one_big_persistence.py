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
	model = 'CAM4-2degree'
	scenario = 'All-Hist'

try:
	sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
	os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')
	working_path='/p/tmp/pepflei/HAPPI/raw_data/'+model+'/'
	home_path = '/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/'
except:
	sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
	home_path = '/global/homes/p/pepflei/persistence_in_models/'

state_dict = {
	'warm':'tas',
	# 'dry':'pr',
	# '5mm':'pr',
	# '10mm':'pr',
	# 'dry-warm':'cpd',
	}

for state,style in state_dict.items():
	all_files=sorted(glob.glob(working_path+scenario+'/'+style+'/_*_'+scenario+'*'+state+'.nc'))

	big_merge = {}
	for key in ['period_length','period_midpoints','period_season','period_monthly_index']:
		big_merge[key] = da.read_nc(all_files[0])[key][:,0:,:]
	big_merge['run_id'] = da.read_nc(all_files[0])['period_season'][:,0:,:].copy()
	big_merge['run_id'].values = 0

	for i_run,file_name in enumerate(all_files[1:]):
		print(file_name)
		for key in ['period_length','period_midpoints','period_season','period_monthly_index']:
			big_merge[key] = da.concatenate((big_merge[key], da.read_nc(file_name)[key][:,0:,:]))
		big_merge['run_id'] = da.read_nc(all_files[key])['period_season'][:,0:,:].copy()
		big_merge['run_id'].values = i_run+1

	da.Dataset(big_merge).write_nc(working_path+scenario+'/'+'_'.join(style,model,scenario,'bigMerge',state)+'.nc')

	del big_merge
	gc.collect()


	'''

	for model in NorESM1 MIROC5 ECHAM6-3-LR CAM4-2degree; do sbatch job_Rscript.sh /p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/analysis_spi/SPI.r /p/tmp/pepflei/HAPPI/raw_data/SPI_stuff/${model}/pr_big_merge.nc pr 3 -13200 -13200 -1 /p/tmp/pepflei/HAPPI/raw_data/SPI_stuff/${model}/pr_big_merge_SPI3.nc; done;

	'''
