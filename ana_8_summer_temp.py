import os,sys,glob,time,collections
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import random as random
import dimarray as da
from subprocess import Popen
import signal

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
from persistence_functions import *

model_dict={'MIROC5':{'grid':'128x256'},
			'NorESM1':{'grid':'192x288'},
			'ECHAM6-3-LR':{'grid':'96x192'},
			'CAM4-2degree':{'grid':'96x144'},
}

os.chdir('/global/homes/p/pepflei/')



import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--overwrite",'-o', help="overwrite output files",default=False)
parser.add_argument('--scenario','-s',help='scneario in Plus20-Future Plus15-Future All-Hist',required=False)
parser.add_argument('--model','-m',help='model',required=False)
parser.add_argument('--region','-r',help='srex region',required=False)
args = parser.parse_args()

if args.model is None:
	models=model_dict.keys()
else:
	models=[args.model]

if args.scenario is None:
	scenarios=['Plus20-Future','Plus15-Future','All-Hist']
else:
	scenarios=[args.scenario]

if args.region is None:
	regions=['ALA','CGI','NEU','NAS','WNA','CNA','ENA','CEU','CAS','TIB','EAS','CAM','MED','WAS']
else:
	regions=[args.region]

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

print args

for scenario in scenarios:
	for model in models:
		# print(model)
		os.chdir('/global/cscratch1/sd/pepflei/'+model+'/')
		# os.system('mkdir tmp')
		# os.system('mkdir tmp/runs')
		# os.system('mkdir tmp/masks')
		# for region in regions:
		# 	os.system('cdo -O select,name='+region+' /global/homes/p/pepflei/masks/srex_mask_'+model+'.nc tmp/masks/'+region+'.nc')
		# all_files=[raw for raw in glob.glob(scenario+'/*') if len(raw.split('/')[-1].split('_'))==7]
		# for id_,in_file in zip([str(ii) for ii in range(len(all_files[:]))],all_files[:]):
		# 	if os.path.isfile('tmp/runs/tmp_'+id_+'_'+scenario+'.nc')==False or args.overwrite:
		# 		print in_file
		# 		signal.signal(signal.SIGALRM, alarm_handler)
		# 		signal.alarm(60)  # 1 minutes
		# 		try:
		# 			os.system('cdo selmon,6,7,8 '+in_file+' tmp/runs/tmp_'+id_+'_'+scenario+'.nc')
		# 			signal.alarm(0)
		# 		except Alarm:
		# 			print "Oops, taking too long!"
        #
		# 	for region in regions:
		# 		if os.path.isfile('tmp/runs/'+id_+'_'+scenario+'_'+region+'.nc')==False or args.overwrite:
		# 			os.system('cdo -L timmean -fldsum -mul tmp/runs/tmp_'+id_+'_'+scenario+'.nc tmp/masks/'+region+'.nc tmp/runs/'+id_+'_'+scenario+'_'+region+'.nc')
        #
		# for region in regions:
		# 	# remove broken files
		# 	os.system('find tmp/runs/ -name "*_'+region+'.nc" -size -1k -delete')
		# 	os.system('cdo -O ensmean tmp/runs/*_'+region+'.nc tmp/tas_'+region+'_'+scenario+'.nc')
		# 	#os.system('rm tmp/runs/*_'+scenario+'.nc')
		# 	#os.system('rm tmp/runs/*_'+scenario+'_'+region+'.nc')


		summer_tas=open('tmp/summer_tas_'+scenario+'.txt','w')
		for region in regions:
			print(Dataset('tmp/tas_'+region+'_'+scenario+'.nc').variables['tas'][:][0][0][0])
			summer_tas.write(region+'\t'+str(Dataset('tmp/tas_'+region+'_'+scenario+'.nc').variables['tas'][:][0][0][0])+'\n')
		summer_tas.close()










#
