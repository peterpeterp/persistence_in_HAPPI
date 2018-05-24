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

if os.path.isdir('/global/cscratch1/sd/pepflei/EKE/'+model)==False: os.system('mkdir '+'/global/cscratch1/sd/pepflei/EKE/'+model)
working_path='/global/cscratch1/sd/pepflei/EKE/'+model+'/'
in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']
full_model=model_dict[model]['full_model']


for scenario,est_thingi in zip(['Plus20-Future','Plus15-Future','All-Hist'],['CMIP5-MMM-est1','CMIP5-MMM-est1','est1']):
	os.system('export SKIP_SAME_TIME=1')
	if os.path.isdir(working_path+scenario)==False: os.system('mkdir '+working_path+scenario)
	os.chdir(working_path+scenario)
	if os.path.isdir(working_path+scenario+'/tmp')==False: os.system('mkdir tmp')
	model_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/'
	version=model_dict[model]['version'][scenario]
	run_list=sorted([path.split('/')[-1] for path in glob.glob(model_path+'day/atmos/tasmax/*')])[0:100]
	for run in run_list:
		FNULL = open(working_path+scenario+'/log_'+run, 'w')

		# u wind
		if os.path.isfile('tmp_ua_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc')==False:
			os.chdir('tmp')
			out=subprocess.Popen('htar -xvf /home/s/stoned/C20C/'+full_model+'/'+scenario+'/'+est_thingi+'/'+version+'/day/atmos/ua/'+run+'/ua_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.tar',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
			os.chdir('../')
			print(glob.glob('tmp/ua*'))
			for tmp_file in glob.glob('tmp/ua*'):
				tmp_file=tmp_file.split('/')[-1]
				subprocess.Popen('cdo -O -sellevel,85000 tmp/'+tmp_file+' tmp/1_'+tmp_file,shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
				subprocess.Popen('cdo -O -setmisstoc,0 tmp/1_'+tmp_file+' tmp/2_'+tmp_file,shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
				subprocess.Popen('cdo -O bandpass,36,180 tmp/2_'+tmp_file+' tmp/3_'+tmp_file,shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

			subprocess.Popen('cdo -O -mergetime tmp/3_ua* tmp_ua_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
			os.system('rm tmp/*')


		# v wind
		if os.path.isfile('tmp_va_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc')==False:
			os.chdir('tmp')
			out=subprocess.Popen('htar -xvf /home/s/stoned/C20C/'+full_model+'/'+scenario+'/'+est_thingi+'/'+version+'/day/atmos/va/'+run+'/va_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.tar',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
			os.chdir('../')
			print(glob.glob('tmp/va*'))
			for tmp_file in glob.glob('tmp/va*'):
				tmp_file=tmp_file.split('/')[-1]
				subprocess.Popen('cdo -O -sellevel,85000 tmp/'+tmp_file+' tmp/1_'+tmp_file,shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
				subprocess.Popen('cdo -O -setmisstoc,0 tmp/1_'+tmp_file+' tmp/2_'+tmp_file,shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
				subprocess.Popen('cdo -O bandpass,36,180 tmp/2_'+tmp_file+' tmp/3_'+tmp_file,shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

			subprocess.Popen('cdo -O -mergetime tmp/3_va* tmp_va_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
			os.system('rm tmp/*')

		# EKE
		subprocess.Popen('cdo -O -merge tmp_ua_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc tmp_va_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc UV_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'_850mbar.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
		subprocess.Popen('cdo expr,EKE="(ua^2+va^2)/2" UV_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'_850mbar.nc EKE_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'_850mbar.nc',shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

		os.system('rm tmp_ua_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc tmp_va_Aday_'+model+'_'+scenario+'_'+est_thingi+'_'+version+'_'+run+'.nc')
