import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
import subprocess as sub

def wait_timeout(proc, seconds):
	"""Wait for a process to finish, or raise exception after timeout"""
	start = time.time()
	end = start + seconds
	interval = min(seconds / 1000.0, .25)

	while True:
		result = proc.poll()
		if result is not None:
			return result
		if time.time() >= end:
			os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
			return 'failed'
		time.sleep(interval)


def try_several_times(command,trials=1,seconds=60):
	for trial in range(trials):
		proc=sub.Popen(command,stdout=sub.PIPE,shell=True, preexec_fn=os.setsid)
		result=wait_timeout(proc,seconds)
		if result!='failed':
			break
	return(result)

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

model=sys.argv[1]
print model

if sys.argv[2] is not None:
	scenarios=[sys.argv[2]]
else:
	scenarios=['Plus20-Future','Plus15-Future','All-Hist']

working_path='/global/cscratch1/sd/pepflei/SPI/'+model+'/'
in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

overwrite=True

os.system('cdo -V')
os.system('export SKIP_SAME_TIME=1')

for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
	selyears={'Plus20-Future':'2106/2115','Plus15-Future':'2106/2115','All-Hist':'2006/2015'}[scenario]
	est_thingi={'Plus20-Future':'CMIP5-MMM-est1','Plus15-Future':'CMIP5-MMM-est1','All-Hist':'est1'}[scenario]
	if os.path.isdir(working_path+scenario)==False: os.system('mkdir '+working_path+scenario)
	version=model_dict[model]['version'][scenario]
	model_path=in_path+scenario+'/*/'+version+'/'
	run_list=model_dict[model]['runs'][scenario]
	for run in run_list:
		# precipitation monthly
		pr_file_name=working_path+scenario+'/'+glob.glob(model_path+'mon/atmos/pr/'+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
		if os.path.isfile(pr_file_name)==False:
			run_files=glob.glob(model_path+'mon/atmos/pr/'+run+'/*')
			if len(run_files)>1:
				command='cdo -O mergetime '
				for subfile in run_files:
					command+=subfile+' '
				result=try_several_times(command+' '+pr_file_name.replace('.nc','_tmp.nc'))
				result=try_several_times('cdo -selyear,'+selyears+' '+pr_file_name.replace('.nc','_tmp.nc')+' '+pr_file_name)
				os.system('rm '+pr_file_name.replace('.nc','_tmp.nc'))
			else:
				result=try_several_times('cdo -O selyear,'+selyears+' '+run_files[0]+' '+pr_file_name)

for scenario in scenarios:
	selyears={'Plus20-Future':'2106/2115','Plus15-Future':'2106/2115','All-Hist':'2006/2015'}[scenario]
	est_thingi={'Plus20-Future':'CMIP5-MMM-est1','Plus15-Future':'CMIP5-MMM-est1','All-Hist':'est1'}[scenario]
	if os.path.isdir(working_path+scenario)==False: os.system('mkdir '+working_path+scenario)
	version=model_dict[model]['version'][scenario]
	model_path=in_path+scenario+'/*/'+version+'/'
	run_list=model_dict[model]['runs'][scenario]
	for run in run_list:
		# precipitation monthly
		if scenario == 'All-Hist':
			pr_file_name=working_path+scenario+'/'+glob.glob(model_path+'mon/atmos/pr/'+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'

			result=try_several_times('Rscript /global/homes/p/pepflei/persistence_in_models/analysis_add/add_61_SPI.r '+\
				pr_file_name+\
				' pr'+\
				' 3 '+\
				selyears.split('/')[0]+' '+\
				selyears.split('/')[0]+' '+\
				selyears.split('/')[1]+' '+\
				working_path+scenario+'/SPI_'+model+'_'+scenario+'_'+run+'.nc',1,1000)

		if scenario != 'All-Hist':
			pr_file_name_fut = working_path+scenario+'/' +glob.glob(model_path+'mon/atmos/pr/'+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			print(working_path+scenario+'/pr_Amon_'+model+'_'+scenario+'*'+run+'.nc')
			pr_file_name_hist = glob.glob(working_path+scenario+'/pr_Amon_'+model+'_'+scenario+'*'+run+'.nc')[0]

			pr_file_name = pr_file_name_fut.replace('.nc','_merged.nc')
			result=try_several_times('cdo mergetime '+' '.join([pr_file_name_hist,pr_file_name_fut,pr_file_name]),1,1000)

			result=try_several_times('Rscript /global/homes/p/pepflei/persistence_in_models/analysis_add/add_61_SPI.r '+\
				pr_file_name+\
				' pr'+\
				' 3 '+\
				' 2006 '+\
				' 2006 '+\
				' 2015 '+\
				working_path+scenario+'/SPI_'+model+'_'+scenario+'_'+run+'_merged.nc',1,1000)



'''
for model in CAM4-2degree ECHAM6-3-LR MIROC5 NorESM1; do for scenario in All-Hist; do nohup python analysis_add/add_62_SPI.py $model $scenario > out/$model+add+$scenario & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done; done;

for model in CAM4-2degree ECHAM6-3-LR MIROC5 NorESM1; do for scenario in Plus20-Future; do nohup python analysis_add/add_62_SPI.py $model $scenario > out/$model+add+$scenario & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done; done;


for model in CAM4-2degree ECHAM6-3-LR MIROC5 NorESM1; do for scenario in All-Hist Plus20-Future; do nohup cdo -ymonmean -ensmean -cat "/global/cscratch1/sd/pepflei/SPI/${model}/${scenario}/SPI*" /global/homes/p/pepflei/data/SPI/SPI_${model}_${scenario}_monClim.nc > out/$model+add & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done; done;


'''
