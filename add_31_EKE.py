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

working_path='/global/cscratch1/sd/pepflei/EKE/'+model+'/'
in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']


for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2116','2106/2116','2006/2016']):
	os.system('export SKIP_SAME_TIME=1')
	if os.path.isdir(working_path+scenario)==False: os.system('mkdir '+working_path+scenario)
	model_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/'
	run_list=sorted([path.split('/')[-1] for path in glob.glob(model_path+'day/atmos/tasmax/*')])[0:100]
	for run in run_list:
		FNULL = open(working_path+scenario+'/log_'+run, 'w')

		out=subprocess.Popen('htar -xvf /home/s/stoned/C20C/MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/ua/'+run_name+'/ua_Aday_MIROC5_All-Hist_est1_v2-0_'+run_name+'.tar',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
		os.chdir('../')
		subprocess.Popen('cdo -O -mergetime raw/ua* ua_Aday_MIROC5_All-Hist_est1_v2-0_'+run_name+'.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
		subprocess.Popen('cdo -O -sellevel,85000 ua_Aday_MIROC5_All-Hist_est1_v2-0_'+run_name+'.nc ua_Aday_MIROC5_All-Hist_est1_v2-0_'+run_name+'_850mbar.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
