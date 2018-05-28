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

if sys.argv[2] is not None:
	scenarios=[sys.argv[2]]
else:
	scenarios=['Plus20-Future','Plus15-Future','All-Hist']

print model,scenarios

if os.path.isdir('/global/cscratch1/sd/pepflei/EKE/'+model)==False: os.system('mkdir '+'/global/cscratch1/sd/pepflei/EKE/'+model)
working_path='/global/cscratch1/sd/pepflei/EKE/'+model+'/'
in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']
full_model=model_dict[model]['full_model']

'''
also use cdo/1.7.0
DIFFERENT FILE STRUCTURES IN TAPE:
check with
hsi -q "cd /home/s/stoned/C20C/NCC/NorESM1-HAPPI/Plus20-Future/CMIP5-MMM-est1/v2-0/day/atmos/ua/run039/ ; ls ; quit"
'''

tape_dict={
	'MIROC5':{
		'Plus20-Future':'/home/s/stoned/C20C/MIROC/MIROC5/Plus20-Future/CMIP5-MMM-est1/***version***/day/atmos/***var***/***run***/***var***_Aday_MIROC5_Plus20-Future_CMIP5-MMM-est1_***version***_***run***.tar',
		'Plus15-Future':'/home/s/stoned/C20C/MIROC/MIROC5/Plus15-Future/CMIP5-MMM-est1/***version***/day/atmos/***var***/***run***/***var***_Aday_MIROC5_Plus15-Future_CMIP5-MMM-est1_***version***_***run***.tar',
		'All-Hist':'/home/s/stoned/C20C/MIROC/MIROC5/All-Hist/est1/***version***/day/atmos/***var***/***run***/***var***_Aday_MIROC5_All-Hist_est1_***version***_***run***.tar'
	},
	'NorESM1':{
		'Plus20-Future':'/home/s/stoned/C20C/NCC/NorESM1-HAPPI/Plus20-Future/CMIP5-MMM-est1/***version***/day/atmos/***var***/***run***/***var***_Aday_NorESM1-HAPPI_Plus20-Future_CMIP5-MMM-est1_***version***_***run***_21060101-21160630.nc',
		'Plus15-Future':'/home/s/stoned/C20C/NCC/NorESM1-HAPPI/Plus15-Future/CMIP5-MMM-est1/***version***/day/atmos/***var***/***run***/***var***_Aday_NorESM1-HAPPI_Plus15-Future_CMIP5-MMM-est1_***version***_***run***_21060101-21160630.nc',
		'All-Hist':'/home/s/stoned/C20C/NCC/NorESM1-HAPPI/All-Hist/est1/***version***/day/atmos/***var***/***run***/***var***_Aday_NorESM1-HAPPI_All-Hist_est1_***version***_***run***.tar'
	},
	'ECHAM6-3-LR':{
		'Plus20-Future':'/home/s/stoned/C20C/MPI-M/ECHAM6-3-LR/Plus20-Future/CMIP5-MMM-est1/***version***/day/atmos/***var***/***run***/***var***_Aday_ECHAM6-3-LR_Plus20-Future_CMIP5-MMM-est1_***version***_***run***_21060101-21151231.nc',
		'Plus15-Future':'/home/s/stoned/C20C/MPI-M/ECHAM6-3-LR/Plus15-Future/CMIP5-MMM-est1/***version***/day/atmos/***var***/***run***/***var***_Aday_ECHAM6-3-LR_Plus15-Future_CMIP5-MMM-est1_***version***_***run***_21060101-21151231.nc',
		'All-Hist':'/home/s/stoned/C20C/MPI-M/ECHAM6-3-LR/All-Hist/est1/***version***/day/atmos/***var***/***run***/***var***_Aday_ECHAM6-3-LR_All-Hist_est1_***version***_***run***.tar'
	},
	'CAM4-2degree':{
		'Plus20-Future':'/home/s/stoned/C20C/ETH/CAM4-2degree/Plus20-Future/CMIP5-MMM-est1/***version***/day/atmos/***var***/***run***/***var***_Aday_CAM4-2degree_Plus20-Future_CMIP5-MMM-est1_***version***_***run***_21060101-21151231.nc',
		'Plus15-Future':'/home/s/stoned/C20C/ETH/CAM4-2degree/Plus15-Future/CMIP5-MMM-est1/***version***/day/atmos/***var***/***run***/***var***_Aday_CAM4-2degree_Plus15-Future_CMIP5-MMM-est1_***version***_***run***_21060101-21151231.nc',
		'All-Hist':'/home/s/stoned/C20C/ETH/CAM4-2degree/All-Hist/est1/***version***/day/atmos/***var***/***run***/***var***_Aday_CAM4-2degree_All-Hist_est1_***version***_***run***.tar'
	},

}


for scenario in scenarios:
	est_thingi={'Plus20-Future':'CMIP5-MMM-est1','Plus15-Future':'CMIP5-MMM-est1','All-Hist':'est1'}[scenario]
	os.system('export SKIP_SAME_TIME=1')
	if os.path.isdir(working_path+scenario)==False: os.system('mkdir '+working_path+scenario)
	os.chdir(working_path+scenario)
	if os.path.isdir(working_path+scenario+'/tmp')==False: os.system('mkdir tmp')
	model_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/'
	version=model_dict[model]['version'][scenario]
	run_list=sorted([path.split('/')[-1] for path in glob.glob(model_path+'day/atmos/tasmax/*')])[0:100]
	for run in run_list:
		if os.path.isfile('EKE_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'_850mbar.nc')==False:
			FNULL = open(working_path+scenario+'/log_'+run, 'w')
			for var in ['ua','va']:
				if os.path.isfile('tmp_'+var+'_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc')==False:
					os.system('rm tmp/'+var+'*'+run+'*')
					os.chdir('tmp')
					if tape_dict[model][scenario].split('.')[-1]=='tar':
						out=subprocess.Popen('htar -xvf '+tape_dict[model][scenario].replace('***var***',var).replace('***version***',version).replace('***run***',run),shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
					if tape_dict[model][scenario].split('.')[-1]=='nc':
						out=subprocess.Popen('hsi -q "get '+tape_dict[model][scenario].replace('***var***',var).replace('***version***',version).replace('***run***',run)+'; quit"',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

					if len(glob.glob(var+'*'+run+'*'))==1:
						orig_file=glob.glob(var+'*'+run+'*')[0]
						subprocess.Popen('cdo -O -splityear '+orig_file+' '+'_'.join([var,model,scenario,run])+'.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
						os.system('rm '+orig_file)

					os.chdir('../')
					for tmp_file in glob.glob('tmp/'+var+'*'+run+'*'):
						tmp_file=tmp_file.split('/')[-1]
						subprocess.Popen('cdo -O -sellevel,85000 tmp/'+tmp_file+' tmp/1_'+tmp_file,shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
						subprocess.Popen('cdo -O -setmisstoc,0 tmp/1_'+tmp_file+' tmp/2_'+tmp_file,shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
						subprocess.Popen('cdo -O bandpass,36,180 tmp/2_'+tmp_file+' tmp/3_'+tmp_file,shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

					subprocess.Popen('cdo -O -mergetime tmp/3_'+var+'* tmp_'+var+'_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
					os.system('rm tmp/'+var+'*'+run+'*')

			# EKE
			subprocess.Popen('cdo -O -merge tmp_ua_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc tmp_va_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc UV_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'_850mbar.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
			subprocess.Popen('cdo expr,EKE="(ua^2+va^2)/2" UV_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'_850mbar.nc EKE_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'_850mbar.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

			os.system('rm tmp_ua_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc tmp_va_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc')
