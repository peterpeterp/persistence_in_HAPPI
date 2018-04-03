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

os.chdir('/global/homes/p/pepflei/')


for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
	for model in model_dict.keys():
		print(model)
		os.chdir('/global/cscratch1/sd/pepflei/'+model+'/')
		os.system('mkdir tmp')
		os.system('mkdir tmp/runs')
		os.system('mkdir tmp/masks')
		all_files=[raw for raw in glob.glob(scenario+'/*') if len(raw.split('/')[-1].split('_'))==7]
		for region in ['ALA','CGI','NEU','NAS','WNA','CNA','ENA','CEU','CAS','TIB','EAS','CAM','MED','WAS']:
			os.system('cdo select,name='+region+' /global/homes/p/pepflei/masks/srex_mask_'+model+'.nc tmp/masks/'+region+'.nc')
			for id_,in_file in zip([str(ii) for ii in range(len(all_files[:]))],all_files[:]):
				os.system('cdo selmon,6,7,8 '+in_file+' tmp/runs/tmp_'+id_+'_'+scenario+'.nc')
				os.system('cdo timmean -fldsum -mul tmp/runs/tmp_'+id_+'.nc tmp/masks/'+region+'.nc tmp/runs/'+id_+'_'+scenario+'_'+region+'.nc')
			os.system('cdo ensmean tmp/runs/*_'+region+'.nc tmp/tas_'+region+'_'+scenario+'.nc')
			os.system('rm tmp/runs/*_'+scenario+'.nc')
			os.system('rm tmp/runs/*_'+scenario+'_'+region+'.nc')
