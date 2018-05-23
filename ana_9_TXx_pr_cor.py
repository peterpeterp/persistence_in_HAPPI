import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da
import subprocess

import __settings

model_dict=__settings.model_dict

model=sys.argv[1]
print model

working_path='/global/cscratch1/sd/pepflei/TXx_pr_cor/'+model+'/'
in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']


for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2116','2106/2116','2006/2016']):
	# if os.path.isdir(working_path+scenario)==False: os.system('mkdir '+working_path+scenario)
	# model_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/'
	# run_list=sorted([path.split('/')[-1] for path in glob.glob(model_path+'day/atmos/tasmax/*')])[0:100]
	# for run in run_list:
	# 	FNULL = open(working_path+scenario+'/log_'+run, 'w')
	#
	# 	# precipitation monthly
	# 	pr_file_name=working_path+scenario+'/'+glob.glob(model_path+'mon/atmos/pr/'+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
	# 	command='cdo -O mergetime '
	# 	for subfile in glob.glob(model_path+'mon/atmos/pr/'+run+'/*'):
	# 		command+='-selyear,'+selyears+' '+subfile+' '
	# 	subprocess.Popen(command+' '+pr_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
	#
	# 	# TXx
	# 	TXx_file_name=working_path+scenario+'/'+glob.glob(model_path+'day/atmos/tasmax/'+run+'/*')[0].split('/')[-1].split(run)[0].replace('tasmax','TXx')+run+'.nc'
	# 	command='cdo -O mergetime '
	# 	for subfile in glob.glob(model_path+'day/atmos/tasmax/'+run+'/*'):
	# 		command+='-selyear,'+selyears+' -monmax '+subfile+' '
	# 	subprocess.Popen(command+' '+TXx_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
	#
	# 	cor_file_name=working_path+scenario+'/'+glob.glob(model_path+'mon/atmos/pr/'+run+'/*')[0].split('/')[-1].split(run)[0].replace('pr','corTXxPr')+run+'.nc'
	# 	subprocess.Popen('cdo -O timcor '+TXx_file_name+' '+pr_file_name+' '+cor_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
	#
	# 	os.system('rm '+pr_file_name+' '+TXx_file_name)

	for pctl in [str(qu) for qu in [0,5,10,50,90,95,100]]:
		subprocess.Popen('cdo -O enspctl,'+pctl+' '+working_path+scenario+'/corTXxPr_* '+working_path+'/corTXxPr_'+model+'_'+scenario+'_'+pctl+'.nc', shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
