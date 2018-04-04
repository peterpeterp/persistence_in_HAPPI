import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import matplotlib.pylab as plt
import dimarray as da
from scipy.optimize import curve_fit
# from lmfit import  Model
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy import stats
import seaborn as sns

os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
import plot_map as plot_map; reload(plot_map)
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence')

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

def percentile_from_counts(y,count,qu):
	if qu>1:
		qu/=100.
	cum=np.cumsum(count)/float(np.sum(count))
	x1=y[cum<qu][-1]
	return x1+(qu-cum[cum<qu][-1])/(cum[cum>qu][0]-cum[cum<qu][-1])

def per_above_qu(y,count,qu):
	if qu>1:
		qu/=100.
	cum=np.cumsum(count)/float(np.sum(count))
	x1=y[cum<qu][-1]
	qu=x1+(qu-cum[cum<qu][-1])/(cum[cum>qu][0]-cum[cum<qu][-1])
	periods=[]
	for ll,cc in zip(y[y>qu],count[y>qu]):
		periods+=[ll]*cc
	return periods

#region_dict=get_regional_distribution('HadGHCND',scenarios=['All-Hist'])
tmp=da.read_nc('data/MIROC5/MIROC5_SummarySummer.nc')['summerStats']
summer_stats=da.DimArray(axes=[['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],tmp.scenario,tmp.region,tmp.variable,tmp.stat],dims=['model','scenario','region','variable','stat'])
for model in summer_stats.model:
	summer_stats[model]=da.read_nc('data/'+model+'/'+model+'_SummarySummer.nc')['summerStats']

NH_regions=['ALA','WNA','CNA','ENA','CGI','CAM','NEU' ,'CEU','CAS','NAS','TIB','EAS','MED','WAS']
NH_regions=['ALA','CGI','NEU' ,'NAS','WNA','CNA','ENA','CEU','CAS','TIB','EAS','CAM','MED','WAS']

summerTas=da.read_nc('data/SummerTas.nc')['summerTas']

big_dict={}
for dataset in ['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	pkl_file = open('data/'+dataset+'/'+dataset+'_regional_distrs.pkl', 'rb')
	big_dict[dataset]=region_dict = pickle.load(pkl_file)	;	pkl_file.close()


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

# plot temps clim
fig,axes = plt.subplots(nrows=4,ncols=1,figsize=(8,8))
for ax,var,title in zip(axes[0:2],['x90_hottest_day','x90_mean_temp'],['hottest day in period','mean temperature during period']):
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
for ax,var,title in zip(axes[2:],['frac_pos_shift','frac_TXx_in_X90'],['fraction of periods with pos shift','fraction of years where TXx in long period']):
	for scenario,color,x_shift in zip(['All-Hist','Plus15-Future','Plus20-Future'],[sns.color_palette()[4],'sandybrown',sns.color_palette()[2]],[-0.3,0,0.3]):
		for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
			tmp=summer_stats[:,scenario,region,var,'mean']
			x+=x_shift
			ax.plot([x],[np.nanmean(tmp,axis=0)],color='k',marker='*')
	ax.set_xticks(np.arange(len(NH_regions))+0.5)
	ax.set_xticklabels(['']*len(NH_regions))
	ax.set_title(title)
ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_stats_clim.png')

# plot temps changes
fig,axes = plt.subplots(nrows=2,ncols=1,figsize=(8,4))
for ax,var,title in zip(axes,['90X_hot_temp','90X_mean_temp'],['hottest day in period','mean temperature during period']):
	for scenario,color in zip(['Plus15-Future','Plus20-Future'],['sandybrown',sns.color_palette()[2]]):
		tmp=summer_stats[:,scenario,:,var,:]-summer_stats[:,'All-Hist',:,var,:]
		for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
			for model,marker in zip(summer_stats.model,['*','^','o','s']):
				ax.plot([x],[tmp[model,region,'mean']],color=color,marker=marker)
		ax.plot(np.arange(len(NH_regions))+0.5,np.nanmean(tmp[:,NH_regions,'mean'],axis=0),color=color,linestyle='-')
	ax.set_xticks(np.arange(len(NH_regions))+0.5)
	ax.set_xticklabels(['']*len(NH_regions))
	ax.set_yticks([-0.5,0,0.5,1,1.5,2,2.5])
	ax.set_ylim((-0.5,2.5))
	ax.set_title(title)

ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_stats_changes.png')


# plot all
plt.close('all')
fig,axes = plt.subplots(nrows=3,ncols=2,figsize=(10,6),gridspec_kw = {'width_ratios':[3,1]})
for ax,var,title in zip(axes[0:2,0],['x90_hottest_day','x90_mean_temp'],['hottest day in long periods','mean temperature during long periods']):
	for scenario,color in zip(['Plus15-Future','Plus20-Future'],['sandybrown',sns.color_palette()[2]]):
		tmp=summer_stats[:,scenario,:,var,:]-summer_stats[:,'All-Hist',:,var,:]
		for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
			for model,marker in zip(summer_stats.model,['*','^','o','s']):
				ax.plot([x],[tmp[model,region,'mean']],color=color,marker=marker)
		ax.plot(np.arange(len(NH_regions))+0.5,np.nanmean(tmp[:,NH_regions,'mean'],axis=0),color=color,linestyle='-')
	ax.set_xticks(np.arange(len(NH_regions))+0.5)
	ax.set_xticklabels(['']*len(NH_regions))
	ax.set_yticks([-0.5,0,0.5,1,1.5,2,2.5])
	ax.set_ylim((-0.5,2.5))
	ax.plot([0,len(NH_regions)],[0,0],'k--')
	ax.set_title(title)

ax=axes[2,0]
for scenario,color in zip(['Plus15-Future','Plus20-Future'],['sandybrown',sns.color_palette()[2]]):
	mod_mean=[]
	for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
		mods=[]
		for model,marker in zip(summer_stats.model,['*','^','o','s']):
			tmp_fu=big_dict[model][region][scenario]['JJA']['warm']
			qu_fu=percentile_from_counts(tmp_fu['period_length'],tmp_fu['count'],95)
			p90_mean_fu=np.mean(per_above_qu(tmp_fu['period_length'],tmp_fu['count'],90))

			tmp_hist=big_dict[model][region]['All-Hist']['JJA']['warm']
			qu_hist=percentile_from_counts(tmp_hist['period_length'],tmp_hist['count'],95)
			p90_mean_hist=np.mean(per_above_qu(tmp_hist['period_length'],tmp_hist['count'],90))

			ax.plot([x],[qu_fu-qu_hist],color=color,marker=marker)
			#ax.plot([x],[p90_mean_fu-p90_mean_hist],color=color,marker=marker)
			mods.append(qu_fu-qu_hist)
		mod_mean.append(np.mean(mods))
	ax.plot(np.arange(len(NH_regions))+0.5,mod_mean,color=color)

ax.set_xlim(0,len(NH_regions)+1)
ax.set_xticks(np.arange(len(NH_regions))+0.5)
ax.set_xticklabels(NH_regions)
ax.plot([0,len(NH_regions)],[0,0],'k--')
ax.set_title('95th percentile')

for ax in axes[:,1]:	ax.axis('off')

ax=axes[1,1]
for scenario,name,color in zip(['Plus15-Future','Plus20-Future'],['+1.5$^\circ$','+2.0$^\circ$'],['sandybrown',sns.color_palette()[2]]):
	for model,marker in zip(summer_stats.model,['*','^','o','s']):
		ax.plot([-90],[0],color=color,marker=marker,linestyle='',label=name+' '+model)

ax.set_xlim((0,1))
ax.legend()

ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_pers_changes.png')


# plot pers only
plt.close('all')
fig,axes = plt.subplots(nrows=1,ncols=2,figsize=(10,3),gridspec_kw = {'width_ratios':[3,1]})

ax=axes[0]
for scenario,color in zip(['Plus15-Future','Plus20-Future'],['sandybrown',sns.color_palette()[2]]):
	mod_mean=[]
	for region,x in zip(NH_regions,np.arange(len(NH_regions))+0.5):
		mods=[]
		for model,marker in zip(summer_stats.model,['*','^','o','s']):
			tmp_fu=big_dict[model][region][scenario]['JJA']['warm']
			qu_fu=percentile_from_counts(tmp_fu['period_length'],tmp_fu['count'],95)
			p90_mean_fu=np.mean(per_above_qu(tmp_fu['period_length'],tmp_fu['count'],90))

			tmp_hist=big_dict[model][region]['All-Hist']['JJA']['warm']
			qu_hist=percentile_from_counts(tmp_hist['period_length'],tmp_hist['count'],95)
			p90_mean_hist=np.mean(per_above_qu(tmp_hist['period_length'],tmp_hist['count'],90))

			ax.plot([x],[qu_fu-qu_hist],color=color,marker=marker)
			#ax.plot([x],[p90_mean_fu-p90_mean_hist],color=color,marker=marker)
			mods.append(qu_fu-qu_hist)
		mod_mean.append(np.mean(mods))
	ax.plot(np.arange(len(NH_regions))+0.5,mod_mean,color=color)

ax.set_xlim(0,len(NH_regions)+1)
ax.set_xticks(np.arange(len(NH_regions))+0.5)
ax.set_xticklabels(NH_regions)
ax.plot([0,len(NH_regions)],[0,0],'k--')
ax.set_title('95th percentile')
ax.set_ylim(axes[0].get_ylim())
ax.set_ylabel('days')
for delim in [4,11]:
	ax.plot([delim,delim],list(axes[0].get_ylim()),'k--')

axes[1].axis('off')

ax=axes[1]
for scenario,name,color in zip(['Plus15-Future','Plus20-Future'],['+1.5$^\circ$','+2.0$^\circ$'],['sandybrown',sns.color_palette()[2]]):
	for model,marker in zip(summer_stats.model,['*','^','o','s']):
		ax.plot([-90],[0],color=color,marker=marker,linestyle='',label=name+' '+model)

ax.set_xlim((0,1))
ax.legend()

ax.set_xticklabels(NH_regions)
plt.savefig('plots/summer_pers_changes.png')






# asd
