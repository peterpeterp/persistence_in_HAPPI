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
summer_stats=da.DimArray(axes=[['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],tmp.scenario,tmp.region,tmp.variable,tmp.stat],dims=['model','scenario','region','variable','stat'])
for model in summer_stats.model:
	summer_stats[model]=da.read_nc('data/'+model+'_SummarySummer.nc')['summerStats']

NH_regions=['ALA','WNA','CNA','ENA','CGI','CAM','NEU' ,'CEU','CAS','NAS','TIB','EAS','MED','WAS']

# write table
table=open('summer_stats.txt','w')
for variable in summer_stats.variable:
	table.write('\n'+variable+'\n')
	table.write('region\tpresent\t+1.5°C\t+2°C\n')
	for region in NH_regions:
		table.write(region)
		for scenario in ['All-Hist','Plus15-Future','Plus20-Future']:
			table.write('\t'+str(np.nanmean(summer_stats[:,scenario,region,variable,'mean'])))
		table.write('\n')
table.close()

# plot
fig,axes = plt.subplots(nrows=2,ncols=1,figsize=(10,8))

for ax,var,title in zip(axes,['90X_hot_temp','90X_mean_temp'],['hottest day in period','fraction of periods with the hottest day lying in the later half of the period']):
	for scenario,color,x_shift in zip(['All-Hist','Plus15-Future','Plus20-Future'],['green','blue','red'],[-0.3,0,0.3]):
		for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
			tmp=summer_stats[:,scenario,region,var,:]-273.15
			x+=x_shift
			ax.fill_between([x-0.15,x+0.15],[np.nanmean(tmp[:,'qu_66l'],axis=0),np.nanmean(tmp[:,'qu_66l'],axis=0)],[np.nanmean(tmp[:,'qu_66h'],axis=0),np.nanmean(tmp[:,'qu_66h'],axis=0)],color=color,alpha=0.3)
			ax.plot([x-0.15,x+0.15],[np.nanmean(tmp[:,'qu_50'],axis=0),np.nanmean(tmp[:,'qu_50'],axis=0)],color='k')
			ax.plot([x],[np.nanmean(tmp[:,'mean'],axis=0)],color='k',marker='*')
	ax.set_xticklabels(['','','','','',''])
	ax.set_title(title)

ax.set_xticks(np.arange(len(NH_regions))+0.5)
ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_stats.png')

# plot
fig,axes = plt.subplots(nrows=2,ncols=1,figsize=(10,8))

for ax,var,title in zip(axes,['90X_hot_temp','90X_mean_temp'],['hottest day in period','fraction of periods with the hottest day lying in the later half of the period']):
	for scenario,color in zip(['Plus15-Future','Plus20-Future'],['green','blue']):
		for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
			tmp=summer_stats[:,scenario,region,var,:]-summer_stats[:,'All-Hist',region,var,:]
			ax.fill_between([x-0.2,x+0.2],[np.nanmean(tmp[:,'qu_66l'],axis=0),np.nanmean(tmp[:,'qu_66l'],axis=0)],[np.nanmean(tmp[:,'qu_66h'],axis=0),np.nanmean(tmp[:,'qu_66h'],axis=0)],color=color,alpha=0.2)
			ax.plot([x-0.2,x+0.2],[np.nanmean(tmp[:,'qu_50'],axis=0),np.nanmean(tmp[:,'qu_50'],axis=0)],color='k')
	ax.set_xticklabels(['','','','','',''])
	ax.set_title(title)

ax.set_xticks(np.arange(len(NH_regions))+0.5)
ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_stats.png')

















# asd
