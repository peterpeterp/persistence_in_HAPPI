import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da



model_dict={'MIROC':{'grid':'128x256','working_path':'/global/cscratch1/sd/pepflei/MIROC/MIROC5/','in_path':'/project/projectdirs/m1517/C20C/MIROC/MIROC5/'},
			'NorESM1':{'grid':'192x288','working_path':'/global/cscratch1/sd/pepflei/NCC/NorESM1-HAPPI/','in_path':'/project/projectdirs/m1517/C20C/NCC/NorESM1-HAPPI/'},
			'ECHAM6-3-LR':{'grid':'96x192','working_path':'/global/cscratch1/sd/pepflei/MPI-M/ECHAM6-3-LR/','in_path':'/project/projectdirs/m1517/C20C/MPI-M/ECHAM6-3-LR/'},
			'CAM4-2degree':{'grid':'96x144','working_path':'/global/cscratch1/sd/pepflei/ETH/CAM4-2degree/','in_path':'/project/projectdirs/m1517/C20C/ETH/CAM4-2degree/'},
}

model=sys.argv[1]
print model

in_path=model_dict[model]['in_path']
working_path=model_dict[model]['working_path']
grid=model_dict[model]['grid']


for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
	os.system('mkdir '+working_path+scenario)
	tmp_path=in_path+scenario+'/*/*/day/atmos/tas/'
	run_list=[path.split('/')[-1] for path in glob.glob(tmp_path+'*')]
	print run_list
	for run in run_list:
		if scenario in ['All-Hist']:
			out_file_name=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			out_file_name_tmp=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'_tmp.nc'
			command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name_tmp
			print command
			os.system(command)
			os.system('cdo -O -selyear,2006/2016 '+out_file_name_tmp+' '+out_file_name)
			os.system('rm '+out_file_name_tmp)
		else:
			out_file_name=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name
			os.system(command)
