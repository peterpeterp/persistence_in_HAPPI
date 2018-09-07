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

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

data_path='data/EOBS/'

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

big_dict={}
for style in ['tas','pr','cpd']:
	pkl_file = open('data/EOBS/'+style+'_EOBS_regional_distrs_srex.pkl', 'rb')
	big_dict[style]= pickle.load(pkl_file)	;	pkl_file.close()
	pkl_file = open('data/EOBS/'+style+'_EOBS_regional_distrs_mid-lat.pkl', 'rb')
	big_dict[style]['NHml']=pickle.load(pkl_file)['mid-lat']	;	pkl_file.close()


NH_regs={

		'NEU':{'hatch':' ','edge':None,'color':'darkgreen','pos_off':(-13,+0),'summer':'JJA','winter':'DJF'},
		'CEU':{'hatch':' ','edge':None,'color':'darkblue','pos_off':(+10,+10),'summer':'JJA','winter':'DJF'},
		'NAS':{'hatch':' ','edge':None,'color':'gray','pos_off':(-50,+5),'summer':'JJA','winter':'DJF'},

		'MED':{'hatch':' ','edge':None,'color':'gray','pos_off':(+18,-5),'summer':'JJA','winter':'DJF'},
		'WAS':{'hatch':' ','edge':None,'color':'darkcyan','pos_off':(+12,+5),'summer':'JJA','winter':'DJF'},
		'NHml':{'hatch':' ','edge':None,'color':'white','edge':'red','pos':(+5,35),'xlabel':'period length [days]','ylabel':'change in exceedence\nprobability [%]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1}
		}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['NHml']={'points':[(-180,23),(180,23),(180,66),(-180,66)]}

colors=['darkred','darkorange','darkmagenta']#+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax):
	subax.axis('off')
	for style,color in zip(['tas','pr','cpd'],colors):
		subax.plot([1,1],[1,1],label=style,c=color)
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
	for style,state,color in zip(['tas','pr','cpd'],['warm','dry','dry-warm'],colors):
		print(style,state)
		tmp=big_dict[style][region]['All-Hist'][season][state]
		count=np.asarray(tmp['count'])/float(sum(tmp['count']))
		pers=tmp['period_length']
		subax.plot(pers,count,color=color)

	subax.annotate('   '+region, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points')


fig,ax_map=srex_overview.srex_overview(distrs,axis_settings,polygons=polygons,reg_info=all_regs,arg1='summer',arg2='warm', x_ext=[-20,80], y_ext=[15,85], small_plot_size=0.25, legend_plot=legend_plot, legend_pos=[163,70], title='warm persistence distributions in JJA',size=6)
plt.savefig('plots/EOBS_compound_distrs.png',dpi=600)
