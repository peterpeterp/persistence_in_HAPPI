import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,num2date
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
		if os.path.isfile(pr_file_name)==False or True:
			command='cdo -O mergetime '
			for subfile in glob.glob(model_path+'mon/atmos/pr/'+run+'/*'):
				command+='-selyear,'+selyears+' '+subfile+' '
			subprocess.Popen(command+' '+pr_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

		# TXx
		TXx_file_name=working_path+scenario+'/'+glob.glob(model_path+'day/atmos/tasmax/'+run+'/*')[0].split('/')[-1].split(run)[0].replace('tasmax','TXx')+run+'.nc'
		if os.path.isfile(TXx_file_name)==False or True:
			command='cdo -O mergetime '
			for subfile in glob.glob(model_path+'day/atmos/tasmax/'+run+'/*'):
				command+='-selyear,'+selyears+' -monmax '+subfile+' '
			subprocess.Popen(command+' '+TXx_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()


	FNULL = open(working_path+scenario+'/log_all', 'w')
	os.system('export SKIP_SAME_TIME=0')
	TXx_file_name=working_path+'TXx_'+model+'_'+scenario+'.nc'
	subprocess.Popen('cdo mergetime '+working_path+scenario+'/TXx_* '+TXx_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
	if os.path.isfile(TXx_file_name) and False:
		os.system('rm '+working_path+scenario+'/TXx_*')

	pr_file_name=working_path+'pr_'+model+'_'+scenario+'.nc'
	subprocess.Popen('cdo mergetime '+working_path+scenario+'/pr_* '+pr_file_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()
	if os.path.isfile(pr_file_name) and False:
		os.system('rm '+working_path+scenario+'/pr_*')

	cor_JJA_name=working_path+'corTXxPr_'+model+'_'+scenario+'_JJA.nc'
	subprocess.Popen('cdo -O timcor -selmon,6/8 '+TXx_file_name+'  -selmon,6/8 '+pr_file_name+' '+cor_JJA_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

	cor_DJF_name=working_path+'corTXxPr_'+model+'_'+scenario+'_DJF.nc'
	subprocess.Popen('cdo -O timcor -selmon,11,12,1 '+TXx_file_name+'  -selmon,11,12,1 '+pr_file_name+' '+cor_DJF_name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()

	# for pctl in [str(qu) for qu in [0,5,10,50,90,95,100]]:
	# 	FNULL = open(working_path+'log_summary', 'w')
	# 	subprocess.Popen('cdo -O enspctl,'+pctl+' '+working_path+scenario+'/corTXxPr_* '+working_path+'/corTXxPr_'+model+'_'+scenario+'_'+pctl+'.nc', shell=True, stdout=FNULL, stderr=subprocess.STDOUT).wait()


'''
bash alternative for NorESM1 ???


pr:
for run in {001..100};do cdo -O -selyear,2106/2116 /project/projectdirs/m1517/C20C/NCC/NorESM1-HAPPI/Plus20-Future/CMIP5-MMM-est1/v2-0/mon/atmos/pr/run${run}/pr_Amon_NorESM1-HAPPI_Plus20-Future_CMIP5-MMM-est1_v2-0_run${run}_210601-211606.nc Plus20-Future/pr_Amon_NorESM1-HAPPI_Plus20-Future_CMIP5-MMM-est1_v2-0_run${run}.nc; done;

TXx:
for run in {001..100};do cdo -O -selyear,2106/2116 -monmax /project/projectdirs/m1517/C20C/NCC/NorESM1-HAPPI/Plus20-Future/CMIP5-MMM-est1/v2-0/day/atmos/tasmax/run${run}/tasmax_Aday_NorESM1-HAPPI_Plus20-Future_CMIP5-MMM-est1_v1-0_run${run}_21060101-21160630.nc Plus20-Future/TXx_Aday_NorESM1-HAPPI_Plus20-Future_CMIP5-MMM-est1_v2-0_run${run}.nc; done;

'''
