import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da
from scipy.optimize import curve_fit
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy import stats

import matplotlib.pylab as plt
import seaborn as sns
sns.set_style("whitegrid")
import matplotlib.ticker as mticker

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

NH_regs={'ALA':{'hatch':' ','edge':None,'color':'darkgreen','pos_off':(+10,+7),'summer':'JJA','winter':'DJF'},
		'WNA':{'hatch':' ','edge':None,'color':'darkblue','pos_off':(+20,+15),'summer':'JJA','winter':'DJF'},
		'CNA':{'hatch':' ','edge':None,'color':'gray','pos_off':(+8,-4),'summer':'JJA','winter':'DJF'},
		'ENA':{'hatch':' ','edge':None,'color':'darkgreen','pos_off':(+18,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'hatch':' ','edge':None,'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},
		'CAM':{'hatch':' ','edge':None,'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'hatch':' ','edge':None,'color':'darkgreen','pos_off':(-13,+0),'summer':'JJA','winter':'DJF'},
		'CEU':{'hatch':' ','edge':None,'color':'darkblue','pos_off':(+10,+5),'summer':'JJA','winter':'DJF'},
		'CAS':{'hatch':' ','edge':None,'color':'darkgreen','pos_off':(+0,+10),'summer':'JJA','winter':'DJF'},
		'NAS':{'hatch':' ','edge':None,'color':'gray','summer':'JJA','winter':'DJF'},
		'TIB':{'hatch':' ','edge':None,'color':'darkcyan','pos_off':(+0,-14),'summer':'JJA','winter':'DJF'},
		'EAS':{'hatch':' ','edge':None,'color':'darkgreen','summer':'JJA','winter':'DJF'},

		'MED':{'hatch':' ','edge':None,'color':'gray','pos_off':(-15,-5),'summer':'JJA','winter':'DJF'},
		'WAS':{'hatch':' ','edge':None,'color':'darkcyan','pos_off':(-5,-5),'summer':'JJA','winter':'DJF'},
		'NHml':{'hatch':' ','edge':'red','color':'white','pos':(-142,37),'xlabel':'period length [days]','ylabel':'exceedence probability [%]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1.3}}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['NHml']={'points':[(-180,23),(180,23),(180,66),(-180,66)]}

colors=['black']+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax):
	subax.axis('off')
	subax.fill_between([1,1],[1,1],[1,1],label='ensemble spread',facecolor='darkmagenta',alpha=0.3)
	subax.plot([1,1],[1,1],label='ensemble mean',color='darkmagenta')
	# subax.fill_between([1,1],[1,1],[1,1],label='dry persistence',facecolor='darkorange',alpha=0.3)
	subax.plot([1,1],[1,1],label='historical warm persistence',color='darkcyan')
	subax.legend(loc='lower right',fontsize=9,ncol=1)

def axis_settings(subax,label='off'):
	subax.set_yscale('log')
	subax.set_xlim((0,35))
	subax.set_ylim((0.0001,1))
	subax.set_xticks([7,14,21,28,35])
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom=label,labelsize=8)
	subax.set_yticks([0.0001,0.001,0.01,0.1,1])
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft=label,labelsize=8)
	locmin = mticker.LogLocator(base=10, subs=[1.0])
	subax.yaxis.set_minor_locator(locmin)
	subax.yaxis.set_minor_formatter(mticker.NullFormatter())
	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)
	return(subax)

def distrs(subax,region,arg1=None,arg2=None,arg3=None):
	season=all_regs[region][arg1]
	ensemble=np.zeros([4,35])*np.nan
	for dataset,color,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['blue','green','magenta','orange'],range(4)):
		tmp_h=big_dict[dataset][region]['All-Hist'][season][arg2]
		count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) for ii in range(len(tmp_h['count']))])
		nmax=min(len(count_h),35)
		ensemble[i,:nmax]=count_h[0:nmax]
	subax.plot(range(1,nmax+1),np.nanmean(ensemble,axis=0),color='darkmagenta')
	subax.fill_between(range(1,nmax+1),np.nanmin(ensemble,axis=0),np.nanmax(ensemble,axis=0),facecolor='darkmagenta',alpha=0.3)

	tmp_h=big_dict['HadGHCND'][region]['All-Hist'][season][arg2]
	count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) for ii in range(len(tmp_h['count']))])
	subax.plot(range(1,len(count_h)+1),count_h,color='darkcyan')
	subax.annotate('   '+region, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points')


fig,ax_map=srex_overview.srex_overview(distrs,axis_settings,polygons=polygons,reg_info=all_regs,arg1='summer',arg2='warm', x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[163,12], title='exceedance probabilites for warm persistence in JJA')
plt.savefig('plots/paper/stats_exceedanceHist.png',dpi=600)
fig,ax_map=srex_overview.srex_overview(distrs,axis_settings,polygons=polygons,reg_info=all_regs,arg1='winter',arg2='cold', x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[163,12], title='exceedance probabilites for cold persistence in DJF')
plt.savefig('plots/paper/stats_exceedanceHist_DJF.png',dpi=600)
