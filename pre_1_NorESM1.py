import os,sys,glob

in_path='/project/projectdirs/m1517/C20C/NCC/NorESM1-HAPPI/'
out_path='/global/cscratch1/sd/pepflei/NCC/NorESM1-HAPPI/'

os.system('mkdir /global/cscratch1/sd/pepflei/NCC')
os.system('mkdir /global/cscratch1/sd/pepflei/NCC/NorESM1-HAPPI')

scenario_list=[path.split('/')[-1] for path in glob.glob(in_path+'*')]

for scenario in scenario_list:
	os.system('mkdir '+out_path+scenario)
	tmp_path=in_path+scenario+'/*/*/day/atmos/tas/'
	run_list=[path.split('/')[-1] for path in glob.glob(tmp_path+'*')]
	print run_list
	for run in run_list:
		if scenario in ['All-Hist']:
			out_file_name=out_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			out_file_name_tmp=out_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'_tmp.nc'
			command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name_tmp
			print command
			os.system(command)
			os.system('cdo -O -selyear,2006/2016 '+out_file_name_tmp+' '+out_file_name)
			os.system('rm '+out_file_name_tmp)
		else:
			out_file_name=out_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'.nc'
			command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name
			os.system(command)
