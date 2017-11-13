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
		out_file_name=glob.glob(tmp_path+run+'/*')[0].split('/')[-1]
		os.system('cp '+tmp_path+run+'/'+out_file_name+' '+out_path+scenario+'/'+out_file_name)		




# in_path='/project/projectdirs/m1517/C20C/MPI-M/ECHAM6-3-LR/'
# out_path='/global/cscratch1/sd/pepflei/MPI-M/ECHAM6-3-LR/'



# htar -xvf /home/s/stoned/C20C/MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/ta/run041/ta_Aday_MIROC5_All-Hist_est1_v2-0_run041.tar