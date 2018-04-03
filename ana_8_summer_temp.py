import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
from persistence_functions import *

model_dict={'MIROC5':{'grid':'128x256'},
			'NorESM1':{'grid':'192x288'},
			'ECHAM6-3-LR':{'grid':'96x192'},
			'CAM4-2degree':{'grid':'96x144'},
}

overwrite=True

try:
	os.chdir('/global/homes/p/pepflei/')
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')


for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
	for model in model_dict.keys():
		all_files=[raw for raw in glob.glob(working_path+scenario+'/*') if len(raw.split('/')[-1].split('_'))==7]
		for region in ['ALA','CGI','NEU','NAS','WNA','CNA','ENA','CEU','CAS','TIB','EAS','CAM','MED','WAS']:
			for in_file in all_files:
				working_path='/global/cscratch1/sd/pepflei/'+model+'/'
				os.system('mkdir tmp')
				os.system('mkdir tmp/runs')
				os.system('cdo timmean -fldsum -mul -selmon,6,7,8 '+in_file+' -select,name='+region+' srex_mask_'+model+'.nc tmp/runs/'+in_file.split('/')[-1].replace('.nc','_reg_av_'+region+'.nc'))
			os.system('cdo ensmean tmp/runs/* tmp/tas_'+region+'.nc')
			asdas
			os.system('rm tmp/runs/*')