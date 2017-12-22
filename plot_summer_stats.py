import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import matplotlib.pylab as plt
import dimarray as da
from scipy.optimize import curve_fit
from lmfit import  Model
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy import stats

os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
import plot_map as plot_map; reload(plot_map)
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()




#region_dict=get_regional_distribution('HadGHCND',scenarios=['All-Hist'])
tmp=da.read_nc('data/MIROC5_SummarySummer.nc')['summerStats']
summer_stats=da.DimArray(axes=[['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],tmp.scenario,tmp.region,tmp.var,tmp.stat],dims=['model','scenario','region','var','stat'])
for model in summer_stats.model:
	summer_stats[model]=da.read_nc('data/'+dataset+'_SummarySummer.nc')['summerStats']

NH_regions=['ALA','WNA','CNA','ENA','CGI','CAM','NEU' ,'CEU','CAS','NAS','TIB','EAS','MED','WAS']

# write table
table=open('summer_stats.txt','w')
for stat in summer_stats.stat:
	table.write('\n'+stat+'\n')
	table.write('region\tpresent\t+1.5°C\t+2°C\n')
	for region in NH_regions:
		table.write(region)
		for scenario in ['All-Hist','Plus15-Future','Plus20-Future']:
			table.write('\t'+str(np.nanmean(summer_stats[:,scenario,region,stat])))
		table.write('\n')
table.close()

# plot
fig,axes = plt.subplots(nrows=2,ncols=1,figsize=(10,8))

for ax,stat,title in zip(axes,['mean_hot_temp','frac_pos_shift'],['hottest day in period','fraction of periods with the hottest day lying in the later half of the period']):
	for scenario in ['All-Hist','Plus15-Future','Plus20-Future']:
		ax.plot(np.arange(len(NH_regions))+0.5,np.nanmean(summer_stats[:,scenario,NH_regions,stat],axis=0))
	ax.set_xticklabels(['','','','','',''])
	ax.set_title(title)

ax.set_xticks(np.arange(len(NH_regions))+0.5)
ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_stats.png')
















# asd
