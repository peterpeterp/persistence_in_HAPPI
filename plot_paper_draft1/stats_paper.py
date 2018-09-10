import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import seaborn as sns
import matplotlib.pylab as plt
import dimarray as da
from scipy.optimize import curve_fit
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy import stats

sys.path.append('/Users/peterpfleiderer/Projects/allgemeine_scripte')
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

if 'big_dict_dry' not in globals():
	big_dict_dry={}
	for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
		pkl_file = open('data/'+dataset+'/pr_'+dataset+'_regional_distrs_srex.pkl', 'rb')
		big_dict_dry[dataset]=region_dict = pickle.load(pkl_file)	;	pkl_file.close()
		pkl_file = open('data/'+dataset+'/pr_'+dataset+'_regional_distrs_mid-lat-SH.pkl', 'rb')
		big_dict_dry[dataset]['SHml']=pickle.load(pkl_file)['mid-lat']	;	pkl_file.close()
		pkl_file = open('data/'+dataset+'/pr_'+dataset+'_regional_distrs_mid-lat.pkl', 'rb')
		big_dict_dry[dataset]['NHml']=pickle.load(pkl_file)['mid-lat']	;	pkl_file.close()

if 'big_dict' not in globals():
	big_dict={}
	for dataset in ['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
		pkl_file = open('data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl', 'rb')
		big_dict[dataset]=region_dict = pickle.load(pkl_file)	;	pkl_file.close()
		pkl_file = open('data/'+dataset+'/'+dataset+'_regional_distrs_mid-lat-SH.pkl', 'rb')
		big_dict[dataset]['SHml']=pickle.load(pkl_file)['mid-lat']	;	pkl_file.close()
		pkl_file = open('data/'+dataset+'/'+dataset+'_regional_distrs_mid-lat.pkl', 'rb')
		big_dict[dataset]['NHml']=pickle.load(pkl_file)['mid-lat']	;	pkl_file.close()

NH_regs={'ALA':{'hatch':' ','color':'darkgreen','pos_off':(+10,+7),'summer':'JJA','winter':'DJF'},
		'WNA':{'hatch':' ','color':'darkblue','pos_off':(+20,+15),'summer':'JJA','winter':'DJF'},
		'CNA':{'hatch':' ','color':'gray','pos_off':(+8,-4),'summer':'JJA','winter':'DJF'},
		'ENA':{'hatch':' ','color':'darkgreen','pos_off':(+18,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'hatch':' ','color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},
		'CAM':{'hatch':' ','color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'hatch':' ','color':'darkgreen','pos_off':(-13,+0),'summer':'JJA','winter':'DJF'},
		'CEU':{'hatch':' ','color':'darkblue','pos_off':(+10,+5),'summer':'JJA','winter':'DJF'},
		'CAS':{'hatch':' ','color':'darkgreen','pos_off':(+0,+10),'summer':'JJA','winter':'DJF'},
		'NAS':{'hatch':' ','color':'gray','summer':'JJA','winter':'DJF'},
		'TIB':{'hatch':' ','color':'darkcyan','pos_off':(+0,-14),'summer':'JJA','winter':'DJF'},
		'EAS':{'hatch':' ','color':'darkgreen','summer':'JJA','winter':'DJF'},

		'MED':{'hatch':' ','color':'gray','pos_off':(-15,-5),'summer':'JJA','winter':'DJF'},
		'WAS':{'hatch':' ','color':'darkcyan','pos_off':(-5,-5),'summer':'JJA','winter':'DJF'},
		'NHml':{'hatch':'///','color':'white','pos':(-142,37),'xlabel':'period length [days]','ylabel':'change in exceedence\nprobability [%]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1.3}}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['NHml']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

maincolor='darkmagenta'

scenario_dict={'HadGHCND':{'early':'1954-1974','late':'1990-2010'},
				'MIROC5':{'early':'All-Hist','late':'Plus20-Future'},
				'NorESM1':{'early':'All-Hist','late':'Plus20-Future'},
				'CAM4-2degree':{'early':'All-Hist','late':'Plus20-Future'},
				'ECHAM6-3-LR':{'early':'All-Hist','late':'Plus20-Future'},
}

# ---------------------------- changes
def legend_plot(subax):
	subax.axis('off')
	# subax.fill_between([1,1],[1,1],[1,1],label='warm persistence',facecolor=maincolor,alpha=0.3)
	# subax.plot([1,1],[1,1],label='warm persistence',color=maincolor)
	# subax.fill_between([1,1],[1,1],[1,1],label='ensemble spread',facecolor='darkorange',alpha=0.3)
	# subax.plot([1,1],[1,1],label='ensemble mean',color='darkorange')
	# subax.plot([1,1],[1,1],label='historical warm persistence',color='darkcyan')
	subax.legend(loc='lower right',fontsize=9,ncol=1)

def axis_settings(subax,label='off'):
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom='off',labelsize=8)
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft='off',labelsize=8)
	return(subax)

def summary_stat(summary):
	counts=summary['count']
	lengths=summary['period_length']
	tmp=[]
	for ll,cc in zip(lengths,counts):
		tmp+=[ll]*cc
	return np.array(tmp)

def scenario_diff(subax,region,arg1=None,arg2=None,arg3=None):
	season=all_regs[region][arg1]

	ensemble=np.zeros([4])*np.nan
	for dataset,color,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['blue','green','magenta','orange'],range(4)):
		ensemble[i]=np.nanmean(summary_stat(big_dict_dry[dataset][region]['All-Hist'][season]['dry']))
	subax.annotate('mean dry:\n'+str(round(np.nanmean(ensemble),02))+' ['+str(round(np.nanmin(ensemble),02))+'-'+str(round(np.nanmax(ensemble),02))+']', xy=(0.01, 0.2), xycoords='axes fraction', fontsize=7,color='darkorange')

	ensemble=np.zeros([4])*np.nan
	for dataset,color,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['blue','green','magenta','orange'],range(4)):
		ensemble[i]=np.nanmean(summary_stat(big_dict[dataset][region]['All-Hist'][season]['warm']))
	subax.annotate('mean warm:\n'+str(round(np.nanmean(ensemble),02))+' ['+str(round(np.nanmin(ensemble),02))+'-'+str(round(np.nanmax(ensemble),02))+']', xy=(0.01, 0.5), xycoords='axes fraction', fontsize=7,color='darkmagenta')

	obs_warm=summary_stat(big_dict['HadGHCND'][region]['All-Hist'][season]['warm'])
	subax.annotate('mean warm obs:\n'+str(round(np.nanmean(obs_warm),02)), xy=(0.01, 0.8), xycoords='axes fraction', fontsize=7,color='darkcyan')

	subax=axis_settings(subax)
	subax.annotate(region, xy=(0.1, 0.02), xycoords='axes fraction', fontsize=10)



fig,ax_map=srex_overview.srex_overview(scenario_diff,axis_settings,polygons=polygons,reg_info=all_regs,arg1='summer',arg2='warm',x_ext=[-180,180],y_ext=[0,85],small_plot_size=0.08,legend_plot=legend_plot, legend_pos=[163,12], title='statistics')
plt.savefig('plots/paper/stats.png',dpi=600)
