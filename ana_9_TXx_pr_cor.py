import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da
import subprocess

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

model=sys.argv[1]
print model

working_path='/global/cscratch1/sd/pepflei/TXx_pr_cor/'+model+'/'
in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']


for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2116','2106/2116','2006/2016']):
	os.system('export SKIP_SAME_TIME=1')
	if os.path.isdir(working_path+scenario)==False: os.system('mkdir '+working_path+scenario)
	model_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/'
	run_list=sorted([path.split('/')[-1] for path in glob.glob(model_path+'day/atmos/tasmax/*')])[0:100]
	for run in run_list:
		FNULL = open(working_path+scenario+'/log_'+run, 'w')

		# precipitation monthly
		pr_file_name=working_path+scenario+'/'+glob.glob(model_path+'mon/atmos/pr/'+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
		command='cdo -O mergetime '
		for subfile in glob.glob(model_path+'mon/atmos/pr/'+run+'/*'):
			command+='-selyear,'+selyears+' '+subfile+' '
		subprocess.Popen(command+' '+pr_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

		# TXx
		TXx_file_name=working_path+scenario+'/'+glob.glob(model_path+'day/atmos/tasmax/'+run+'/*')[0].split('/')[-1].split(run)[0].replace('tasmax','TXx')+run+'.nc'
		command='cdo -O mergetime '
		for subfile in glob.glob(model_path+'day/atmos/tasmax/'+run+'/*'):
			command+='-selyear,'+selyears+' -monmax '+subfile+' '
		subprocess.Popen(command+' '+TXx_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

	FNULL = open(working_path+scenario+'/log_all', 'w')
	os.system('export SKIP_SAME_TIME=0')
	TXx_file_name=working_path+'TXx_'+model+'_'+scenario+'.nc'
	subprocess.Popen('cdo mergetime '+working_path+scenario+'/TXx_* '+TXx_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
	os.system('rm '+working_path+scenario+'/TXx_*')
	pr_file_name=working_path+'pr_'+model+'_'+scenario+'.nc'
	subprocess.Popen('cdo mergetime '+working_path+scenario+'/pr_* '+pr_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
	os.system('rm '+working_path+scenario+'/pr_*')

	cor_JJA_name=working_path+'corTXxPr_'+model+'_'+scenario+'_JJA.nc'
	subprocess.Popen('cdo -O timcor -selmon,6/8 '+TXx_file_name+'  -selmon,6/8 '+pr_file_name+' '+cor_JJA_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

	cor_JJA_name=working_path+'corTXxPr_'+model+'_'+scenario+'_JJA.nc'
	subprocess.Popen('cdo -O timcor -selmon,11,12,1 '+TXx_file_name+'  -selmon,11,12,1 '+pr_file_name+' '+cor_JJA_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

	# for pctl in [str(qu) for qu in [0,5,10,50,90,95,100]]:
	# 	FNULL = open(working_path+'log_summary', 'w')
	# 	subprocess.Popen('cdo -O enspctl,'+pctl+' '+working_path+scenario+'/corTXxPr_* '+working_path+'/corTXxPr_'+model+'_'+scenario+'_'+pctl+'.nc', shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
