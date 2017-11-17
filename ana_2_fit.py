import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import matplotlib.pylab as plt
import dimarray as da

from scipy.optimize import curve_fit

from lmfit import  Model

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

os.chdir('../weather_persistence')
from persistence_support import *
os.chdir('../HAPPI_persistence')

model=sys.argv[1]
print model

scenarios=['Plus20-Future','Plus15-Future','All-Hist']
seasons=['MAM','JJA','SON','DJF','year']
states=['cold','warm']
types=['sing_b','sing_a','sing_BIC','sing_error','doub_b1','doub_b2','doub_a1','doub_thr','doub_BIC','doub_error']

big_dict={}
for scenario in ['All-Hist','Plus15-Future','Plus20-Future']:
	pkl_file = open('data/'+dataset+'_'+scenario+'_counter.pkl', 'rb')
	big_dict[scenario] = pickle.load(pkl_file)	;	pkl_file.close()

lat=big_dict[scenario]['lat']
lon=big_dict[scenario]['lon']

SummaryFit=da.DimArray(axes=[np.asarray(scenarios),np.asarray(seasons),np.asarray(states),np.asarray(types),lat,lon],dims=['scenario','season','state','type','lat','lon'])

for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
	distr_dict = big_dict[scenario]

	for iy in range(len(lat)):
		for ix in range(len(lon)):
			grid_cell=distr_dict[str(lat[iy])+'_'+str(lon[ix])]
			grid_cell['year']=grid_cell['MAM']+grid_cell['JJA']+grid_cell['SON']+grid_cell['DJF']

	for season in seasons:
		print season
		for iy in range(len(lat)):
			print iy
			for ix in range(len(lon)):
				counter=distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]

				if len(counter.keys())>20:
					for state,state_name in zip([-1,1],['cold','warm']):
						pers_tmp=np.array(range(1,max([state*key+1 for key in counter.keys()])))
						count,pers=[],[]
						for pp,i in zip(pers_tmp,range(len(pers_tmp))):
							if pp*state in counter.keys():
								count.append(counter[pp*state])
								pers.append(pp)
						count=np.array(count)
						pers=np.array(pers)

						tmp=all_fits(count,pers,plot=False)

						SummaryFit[scenario][season][state_name]['sing_b'][lat[iy]][lon[ix]]=tmp['single_exp']['params']['b1']
						SummaryFit[scenario][season][state_name]['sing_a'][lat[iy]][lon[ix]]=tmp['single_exp']['params']['a1']
						SummaryFit[scenario][season][state_name]['sing_BIC'][lat[iy]][lon[ix]]=tmp['single_exp']['bic']

						SummaryFit[scenario][season][state_name]['doub_b1'][lat[iy]][lon[ix]]=tmp['double_exp']['params']['b1']
						SummaryFit[scenario][season][state_name]['doub_b2'][lat[iy]][lon[ix]]=tmp['double_exp']['params']['b2']
						SummaryFit[scenario][season][state_name]['doub_a1'][lat[iy]][lon[ix]]=tmp['double_exp']['params']['a1']
						SummaryFit[scenario][season][state_name]['doub_thr'][lat[iy]][lon[ix]]=tmp['double_exp']['params']['thr']
						SummaryFit[scenario][season][state_name]['doub_BIC'][lat[iy]][lon[ix]]=tmp['double_exp']['bic']


ds=da.Dataset({'SummaryFit':SummaryFit})
ds.write_nc('data/'+dataset+'_SummaryFit.nc', mode='w')
