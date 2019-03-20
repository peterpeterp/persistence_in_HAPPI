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

try:
	model=sys.argv[1]
	print model

except:
	model = 'CAM4-2degree'


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

all_files_hist=sorted(glob.glob(working_path+'All-Hist'+'/pr_Amon_*_'+'All-Hist'+'*'+'.nc'))
all_files_fut=sorted(glob.glob(working_path+'Plus20-Future'+'/pr_Amon_*_'+'Plus20-Future'+'*'+'.nc'))

dummy = da.read_nc(all_files_hist[0])['pr'].squeeze()

big_merge_hist = dummy
big_merge_fut = dummy
land_mask=da.read_nc('/global/homes/p/pepflei/masks/landmask_'+grid+'_NA-1.nc')['landmask']

empty_year = dummy.values[:12,:,:].copy() * np.nan
big_merge_hist = np.concatenate((big_merge_hist, empty_year))
big_merge_fut = np.concatenate((big_merge_fut, empty_year))

empti_spi = da.Dataset({'SPI3':dummy.copy() * np.nan})

for file_hist,file_fut in zip(all_files_hist[1:],all_files_fut[1:]):
	print(file_hist,file_fut)
	big_merge_hist = np.concatenate((big_merge_hist, da.read_nc(file_hist)['pr'].squeeze()))
	big_merge_hist = np.concatenate((big_merge_hist, empty_year))
	big_merge_fut = np.concatenate((big_merge_fut, da.read_nc(file_fut)['pr'].squeeze()))
	big_merge_fut = np.concatenate((big_merge_fut, empty_year))


if big_merge_hist.shape[0] != 13200 or big_merge_fut.shape[0] != 13200:
	asdas

os.system('mkdir '+working_path+'grid_level/')

lat,lon = da.read_nc(file_hist)['pr'].lat,da.read_nc(file_hist)['pr'].lon
constructed_time_axis = np.append(np.arange(-132*100,0), np.arange(132*100))
for iy,y in enumerate(lat):
	for ix,x in enumerate(lon):
		if land_mask[y,x] != 1 and y>=0:
			start = time.time()
			print(y,x)
			grid_file_name = working_path+'grid_level/'+str(y)+'_'+str(x)+'.txt'
			tmp = np.append(big_merge_hist[:,iy,ix],big_merge_fut[:,iy,ix])
			csv = open(grid_file_name,'w')
			csv.write(';'.join([str(i) for i in tmp]))
			csv.close()

			print(time.time() -start)

			result=try_several_times('Rscript /global/homes/p/pepflei/persistence_in_models/analysis_add/add_61_SPI_single.r '+\
				grid_file_name+' '+\
				grid_file_name.replace('.txt','_SPI3.txt'),1,1000)

			print(time.time() -start)

print('----------- saving stuff')
for file_hist,file_fut,fi in zip(all_files_hist,all_files_fut,range(len(all_files_hist))):
	out_hist = dummy.copy()*np.nan
	out_fut = dummy.copy()*np.nan
	for iy,y in enumerate(lat):
		for ix,x in enumerate(lon):
			if land_mask[y,x] != 1 and y>=0:
				csv = open(working_path+'grid_level/'+str(y)+'_'+str(x)+'_SPI3.txt','r').read()
				tmp_spi = np.array([])
				for dd in csv.split(';'):
					if dd == 'NA':
						tmp_spi = np.append(tmp_spi,np.nan)
					else:
						tmp_spi = np.append(tmp_spi,np.float(dd.replace('"','')))

				indices = np.arange(fi*11*12+2 ,(fi+1)*11*12 -12)
				out_hist.ix[2:,iy,ix] = tmp_spi[indices]
				out_fut.ix[2:,iy,ix] = tmp_spi[indices + 13200]

	da.Dataset({'SPI3':out_hist}).write_nc(file_hist.replace('pr','SPI3'))
	da.Dataset({'SPI3':out_fut}).write_nc(file_fut.replace('pr','SPI3'))



'''
for model in CAM4-2degree ECHAM6-3-LR MIROC5 NorESM1; do nohup python analysis_add/add_62_SPI_merged.py $model > out/$model+spi & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done;

for model in CAM4-2degree ECHAM6-3-LR MIROC5 NorESM1; do for scenario in Plus20-Future; do nohup python analysis_add/add_62_SPI.py $model $scenario > out/$model+add+$scenario & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done; done;


for model in CAM4-2degree ECHAM6-3-LR MIROC5 NorESM1; do for scenario in All-Hist Plus20-Future; do nohup cdo -ymonmean -ensmean -cat "/global/cscratch1/sd/pepflei/SPI/${model}/${scenario}/SPI*" /global/homes/p/pepflei/data/SPI/SPI_${model}_${scenario}_monClim.nc > out/$model+add & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }; done; done;


'''
