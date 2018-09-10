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
import matplotlib.ticker as mticker
import seaborn as sns
sns.set_style("whitegrid", {'grid.linestyle': '--'})

sys.path.append('/Users/peterpfleiderer/Projects/allgemeine_scripte')
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

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
polygons['NHml']={'points':[(-180,23),(180,23),(180,66),(-180,66)]}

colors=['black']+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax):
	subax.axis('off')
	for dataset,color in zip(['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],colors):
		subax.plot([1,1],[1,1],label=dataset,c=color)
	subax.legend(loc='best',fontsize=9)

def axis_settings(subax,label='off'):
	subax.set_yscale('log')
	subax.set_xlim((0,40))
	subax.set_ylim((0.0001,0.5))
	subax.set_xticks([7,14,21,28,35])
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom=label,labelsize=8)
	subax.set_yticks([0.0001,0.001,0.01,0.1,1])
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft=label,labelsize=8)
	locmin = mticker.LogLocator(base=10,subs=[1.0]) # subs=np.arange(0.2,1,0.2),numticks=5
	subax.yaxis.set_minor_locator(locmin)
	subax.yaxis.set_minor_formatter(mticker.NullFormatter())
	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)
	return(subax)

def distrs(subax,region,arg1=None,arg2=None,arg3=None):
	season=all_regs[region][arg1]
	for dataset,color in zip(['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],colors):
		try:
			tmp=big_dict[dataset][region]['All-Hist'][season][arg2]
			count=np.asarray(tmp['count'])/float(sum(tmp['count']))
			pers=tmp['period_length']
			subax.plot(pers,count,color=color)
		except:
			pass
	subax.annotate('   '+region, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points')


fig,ax_map=srex_overview.srex_overview(distrs,axis_settings,polygons=polygons,reg_info=all_regs,arg1='summer',arg2='warm', x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[163,70], title='warm persistence distributions in JJA')
plt.savefig('plots/paper/Figure1.png',dpi=600)
