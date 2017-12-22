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
import seaborn as sns

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
NH_regions=['ALA','CGI','NEU' ,'NAS','WNA','CNA','ENA','CEU','CAS','TIB','EAS','CAM','MED','WAS']

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

# plot temps
fig,axes = plt.subplots(nrows=2,ncols=1,figsize=(8,4))
for ax,var,title in zip(axes,['90X_hot_temp','90X_mean_temp'],['hottest day in period','mean temperature during period']):
	for scenario,color,x_shift in zip(['All-Hist','Plus15-Future','Plus20-Future'],[sns.color_palette()[4],'sandybrown',sns.color_palette()[2]],[-0.3,0,0.3]):
		for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
			tmp=summer_stats[:,scenario,region,var,:]-273.15
			x+=x_shift
			ax.fill_between([x-0.15,x+0.15],[np.nanmean(tmp[:,'qu_66l'],axis=0),np.nanmean(tmp[:,'qu_66l'],axis=0)],[np.nanmean(tmp[:,'qu_66h'],axis=0),np.nanmean(tmp[:,'qu_66h'],axis=0)],color=color)
			ax.plot([x-0.15,x+0.15],[np.nanmean(tmp[:,'qu_50'],axis=0),np.nanmean(tmp[:,'qu_50'],axis=0)],color='k')
			ax.plot([x],[np.nanmean(tmp[:,'mean'],axis=0)],color='k',marker='*')
	ax.set_xticks(np.arange(len(NH_regions))+0.5)
	ax.set_xticklabels(['']*len(NH_regions))
	ax.set_title(title)

ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_stats.png')

# plot temps
fig,axes = plt.subplots(nrows=2,ncols=1,figsize=(8,4))
for ax,var,title in zip(axes,['90X_hot_temp','90X_mean_temp'],['hottest day in period','mean temperature during period']):
	for scenario,color in zip(['Plus15-Future','Plus20-Future'],['sandybrown',sns.color_palette()[2]]):
		for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
			tmp=summer_stats[:,scenario,region,var,:]-summer_stats[:,'All-Hist',region,var,:]
			ax.plot([x],[np.nanmean(tmp[:,'mean'],axis=0)],color=color,marker='*')
			#ax.plot([x],[np.nanmean(tmp[:,'qu_100'],axis=0)],color=color,marker='*')
	ax.set_xticks(np.arange(len(NH_regions))+0.5)
	ax.set_xticklabels(['']*len(NH_regions))
	ax.set_yticks([0,0.5,1,1.5,2])
	ax.set_ylim((0,2))
	ax.set_title(title)

ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_stats_changes.png')


big_dict={}
for dataset in ['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	pkl_file = open('data/'+dataset+'_regional_distrs.pkl', 'rb')
	big_dict[dataset]=region_dict = pickle.load(pkl_file)	;	pkl_file.close()

def percentile_from_counts(y,count,qu):
	if qu>1:
		qu/=100.
	cum=np.cumsum(count)/float(np.sum(count))
	x1=y[cum<qu][-1]
	return x1+(qu-cum[cum<qu][-1])/(cum[cum>qu][0]-cum[cum<qu][-1])

# plot pers
fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(8,4))
for scenario,color in zip(['Plus15-Future','Plus20-Future'],['sandybrown',sns.color_palette()[2]]):
	for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
		for model,marker in zip(summer_stats.model,['*','^','o','s']):
			tmp_fu=big_dict[model][region][scenario]['JJA']['warm']
			qu_fu=percentile_from_counts(tmp_fu['period_length'],tmp_fu['count'],95)
			tmp_hist=big_dict[model][region]['All-Hist']['JJA']['warm']
			qu_hist=percentile_from_counts(tmp_hist['period_length'],tmp_hist['count'],95)
			ax.plot([x],[qu_fu-qu_hist],color=color,marker=marker)
		#ax.plot([x],[np.nanmean(tmp[:,'qu_100'],axis=0)],color=color,marker='*')
ax.set_xticks(np.arange(len(NH_regions))+0.5)
ax.set_xticklabels(['']*len(NH_regions))
ax.plot([0,len(NH_regions)],[0,0],'k--')
#ax.set_yticks([0,0.5,1,1.5,2])
#ax.set_ylim((0,2))
ax.set_title('Changes in the 95th percentile of warm periods in JJA')

ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_pers_changes.png')








# asd
