import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da
import subprocess



model_dict={'MIROC5':{'grid':'128x256','working_path':'/global/cscratch1/sd/pepflei/TXx_pr_cor/MIROC5/','in_path':'/project/projectdirs/m1517/C20C/MIROC/MIROC5/','version':{'Plus20-Future':'v2-0','Plus15-Future':'v2-0','All-Hist':'v1-0'}},
			'NorESM1':{'grid':'192x288','working_path':'/global/cscratch1/sd/pepflei/TXx_pr_cor/NorESM1/','in_path':'/project/projectdirs/m1517/C20C/NCC/NorESM1-HAPPI/','version':{'Plus20-Future':'v1-0','Plus15-Future':'v1-0','All-Hist':'v1-0'}},
			'ECHAM6-3-LR':{'grid':'96x192','working_path':'/global/cscratch1/sd/pepflei/TXx_pr_cor/ECHAM6-3-LR/','in_path':'/project/projectdirs/m1517/C20C/MPI-M/ECHAM6-3-LR/','version':{'Plus20-Future':'v2-0','Plus15-Future':'v2-0','All-Hist':'v1-0'}},
			'CAM4-2degree':{'grid':'96x144','working_path':'/global/cscratch1/sd/pepflei/TXx_pr_cor/CAM4-2degree/','in_path':'/project/projectdirs/m1517/C20C/ETH/CAM4-2degree/','version':{'Plus20-Future':'v2-0','Plus15-Future':'v2-0','All-Hist':'v1-0'}},
}

model=sys.argv[1]
print model

in_path=model_dict[model]['in_path']
working_path=model_dict[model]['working_path']
grid=model_dict[model]['grid']


for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2116','2106/2116','2006/2016']):
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

		cor_file_name=working_path+scenario+'/'+glob.glob(model_path+'mon/atmos/pr/'+run+'/*')[0].split('/')[-1].split(run)[0].replace('pr','corTXxPr')+run+'.nc'
		subprocess.Popen('cdo -O timcor '+TXx_file_name+' '+pr_file_name+' '+cor_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

		os.system('rm '+pr_file_name+' '+TXx_file_name)
