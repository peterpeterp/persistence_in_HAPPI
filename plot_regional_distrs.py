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
#import plot_map as plot_map; reload(plot_map)
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence')

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()




#region_dict=get_regional_distribution('HadGHCND',scenarios=['All-Hist'])

big_dict={}
for dataset in ['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	pkl_file = open('data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl', 'rb')
	big_dict[dataset]=region_dict = pickle.load(pkl_file)	;	pkl_file.close()






# ---------------------------- distr comparison
def legend_plot(subax):
	subax.axis('off')
	for dataset,color in zip(['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['black','blue','green','magenta','orange']):
		subax.plot([1,1],[1,1],label=dataset,c=color)
	subax.legend(loc='best',fontsize=12)

def axis_settings(subax,label='off'):
	subax.set_yscale('log')
	subax.set_xlim((0,40))
	subax.set_ylim((0.0001,0.5))
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom=label)
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft=label)
	subax.locator_params(axis = 'x', nbins = 5)
	return(subax)

def distrs(subax,region,arg1=None,arg2=None,arg3=None):
	for dataset,color in zip(['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['black','blue','green','magenta','orange']):
		try:
			tmp=big_dict[dataset][region]['All-Hist'][arg1][arg2]
			count=np.asarray(tmp['count'])/float(sum(tmp['count']))
			pers=tmp['period_length']
			subax.plot(pers,count,color=color)
		except:
			pass
	axis_settings(subax)
	subax.annotate('   '+region, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')

for season in ['JJA','DJF']:
	for state in ['warm','cold']:
		fig=srex_overview.srex_overview(distrs,srex_polygons=srex,annotate_plot=annotate_plot,arg1=season,arg2=state)

		ax = fig.add_axes([0.0, 0.0, 0.1, 0.1333333333]); ax.axis('off'); ax.text(0.5,0.5,season+' '+state,fontsize=14)

		ax = fig.add_axes([0.09, 0.2, 0.1, 0.1333333333])
		for dataset,color in zip(['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['black','blue','green','magenta','orange']):
			pkl_file = open('data/'+dataset+'/'+dataset+'_regional_distrs_mid-lat.pkl', 'rb')
			mid_lat=pickle.load(pkl_file)	;	pkl_file.close()
			tmp=mid_lat['mid-lat']['All-Hist'][season][state]
			count=np.asarray(tmp['count'])/float(sum(tmp['count']))
			pers=tmp['period_length']
			ax.plot(pers,count,color=color)
		ax=axis_settings(ax,label='on')
		ax.set_ylabel('PDF')
		ax.set_xlabel('days')
		ax.set_title('NH mid-latitudes')

		ax = fig.add_axes([0.09, 0.4, 0.1, 0.1333333333])
		for dataset,color in zip(['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['black','blue','green','magenta','orange']):
			pkl_file = open('data/'+dataset+'/'+dataset+'_regional_distrs_mid-lat-SH.pkl', 'rb')
			mid_lat=pickle.load(pkl_file)	;	pkl_file.close()
			tmp=mid_lat['mid-lat']['All-Hist'][season][state]
			count=np.asarray(tmp['count'])/float(sum(tmp['count']))
			pers=tmp['period_length']
			ax.plot(pers,count,color=color)
		ax=axis_settings(ax,label='on')
		ax.set_ylabel('PDF')
		ax.set_xlabel('days')
		ax.set_title('SH mid-latitudes')

		plt.savefig('plots/distrs_'+season+'_'+state+'.png',dpi=600)




# ---------------------------- changes
def legend_plot(subax):
	subax.axis('off')
	for dataset,color in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['blue','green','magenta','orange']):
		subax.fill_between([1,1],[1,1],[1,1],label=dataset,facecolor=color,alpha=0.3)
	subax.legend(loc='best',fontsize=12)

def axis_settings(subax,label='off'):
	subax.set_xlim((0,30))
	subax.set_ylim((-10,10))
	subax.plot([0,40],[0,0],'k')
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom=label)
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft=label)
	subax.locator_params(axis = 'y', nbins = 5)
	subax.locator_params(axis = 'x', nbins = 5)
	return(subax)

def scenario_diff(subax,region,arg1=None,arg2=None,arg3=None):
	for dataset,color in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['blue','green','magenta','orange']):
		tmp_20=big_dict[dataset][region]['Plus20-Future'][arg1][arg2]
		tmp_h=big_dict[dataset][region]['All-Hist'][arg1][arg2]
		count_20=np.asarray(tmp_20['count'])/float(np.nansum(tmp_20['count']))
		count_h=np.asarray(tmp_h['count'])/float(np.nansum(tmp_h['count']))
		nmax=min(len(count_20),len(count_h),40)
		subax.fill_between(tmp_h['period_length'][0:nmax],(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100,tmp_h['period_length'][0:nmax]*0,facecolor=color,alpha=0.3)
	subax=axis_settings(subax)
	subax.annotate('              '+region, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')


for season in ['JJA','DJF']:
	for state in ['warm','cold']:
		fig=srex_overview.srex_overview(scenario_diff,srex_polygons=srex,annotate_plot=annotate_plot,arg1=season,arg2=state)

		ax = fig.add_axes([0.0, 0.0, 0.1, 0.1333333333]); ax.axis('off'); ax.text(0.5,0.5,season+' '+state,fontsize=14)

		subax = fig.add_axes([0.09, 0.2, 0.1, 0.1333333333])
		for dataset,color in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['blue','green','magenta','orange']):
			pkl_file = open('data/'+dataset+'/'+dataset+'_regional_distrs_mid-lat.pkl', 'rb')
			mid_lat=pickle.load(pkl_file)	;	pkl_file.close()
			tmp_20=mid_lat['mid-lat']['Plus20-Future'][season][state]
			tmp_h=mid_lat['mid-lat']['All-Hist'][season][state]
			count_20=np.asarray(tmp_20['count'])/float(np.nansum(tmp_20['count']))
			count_h=np.asarray(tmp_h['count'])/float(np.nansum(tmp_h['count']))
			nmax=min(len(count_20),len(count_h),40)
			subax.fill_between(tmp_h['period_length'][0:nmax],(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100,tmp_h['period_length'][0:nmax]*0,facecolor=color,alpha=0.3)
		subax=axis_settings(subax,label='on')
		subax.set_title('NH mid-latitudes')
		subax.set_ylabel('change [$\%$]')
		subax.set_xlabel('days')

		subax = fig.add_axes([0.09, 0.4, 0.1, 0.1333333333])
		for dataset,color in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['blue','green','magenta','orange']):
			pkl_file = open('data/'+dataset+'/'+dataset+'_regional_distrs_mid-lat-SH.pkl', 'rb')
			mid_lat=pickle.load(pkl_file)	;	pkl_file.close()
			tmp_20=mid_lat['mid-lat']['Plus20-Future'][season][state]
			tmp_h=mid_lat['mid-lat']['All-Hist'][season][state]
			count_20=np.asarray(tmp_20['count'])/float(np.nansum(tmp_20['count']))
			count_h=np.asarray(tmp_h['count'])/float(np.nansum(tmp_h['count']))
			nmax=min(len(count_20),len(count_h),40)
			subax.fill_between(tmp_h['period_length'][0:nmax],(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100,tmp_h['period_length'][0:nmax]*0,facecolor=color,alpha=0.3)
		subax=axis_settings(subax,label='on')
		subax.set_title('SH mid-latitudes')
		subax.set_ylabel('change [$\%$]')
		subax.set_xlabel('days')

		plt.savefig('plots/distr_changes_'+season+'_'+state+'.png',dpi=600)
