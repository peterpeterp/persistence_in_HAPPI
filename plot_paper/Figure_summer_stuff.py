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
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
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

data = da.read_nc('data/tas_summerStat_srex.nc')


NH_regs={'ALA':{'color':'darkgreen','pos_off':(+10,+7),'summer':'JJA','winter':'DJF'},
		'WNA':{'color':'darkblue','pos_off':(+20,+15),'summer':'JJA','winter':'DJF'},
		'CNA':{'color':'gray','pos_off':(+8,-4),'summer':'JJA','winter':'DJF'},
		'ENA':{'color':'darkgreen','pos_off':(+18,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},
		'CAM':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'color':'darkgreen','pos_off':(-13,+0),'summer':'JJA','winter':'DJF'},
		'CEU':{'color':'darkblue','pos_off':(+9,+5),'summer':'JJA','winter':'DJF'},
		'CAS':{'color':'darkgreen','pos_off':(-8,+10),'summer':'JJA','winter':'DJF'},
		'NAS':{'color':'gray','summer':'JJA','winter':'DJF'},
		'TIB':{'color':'darkcyan','pos_off':(+2,-4),'summer':'JJA','winter':'DJF'},
		'EAS':{'color':'darkgreen','summer':'JJA','winter':'DJF'},

		'MED':{'color':'gray','pos_off':(-15,-5),'summer':'JJA','winter':'DJF'},
		'WAS':{'color':'darkcyan','pos_off':(-5,-5),'summer':'JJA','winter':'DJF'},
		'NHml':{'edge':'darkblue','color':'none','alpha':1,'pos':(-142,42),'xlabel':'','ylabel':'temperature change [K]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1.3}}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['NHml']={'points':[(-180,23),(180,23),(180,66),(-180,66)]}

colors=['black']+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None):
	subax.axis('off')
	legend_elements=[]
	legend_elements.append(Patch(facecolor='orange', alpha=0.3, label='+1.5$^\circ$C vs 2006-2015'))
	legend_elements.append(Patch(facecolor='red', alpha=0.3, label='+2$^\circ$C vs 2006-2015'))
	legend_elements.append(Line2D([0], [0], color='k', label='ensemble mean'))

	subax.legend(handles=legend_elements, loc='lower right',fontsize=9, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)


def axis_settings(subax,label=False):
	subax.set_xlim((0.5,3.5))
	subax.set_ylim((0.0,2.5))
	subax.set_xticks(range(1,4))
	subax.set_xticklabels(['seas. mean','period mean\n(+14 day periods)','hottest day\n(+14 day periods)'])
	subax.tick_params(axis='x',which='both',bottom=True,top=True,labelbottom=label,labelsize=8,rotation=90)
	subax.set_yticks([0.5,1,1.5,2])
	subax.tick_params(axis='y',which='both',left=True,right=True,labelleft=label,labelsize=8)
	locmin = mticker.LogLocator(base=10, subs=[1.0])
	subax.yaxis.set_minor_locator(locmin)
	subax.yaxis.set_minor_formatter(mticker.NullFormatter())
	subax.yaxis.get_label().set_backgroundcolor('w')
	for tick in subax.yaxis.get_major_ticks()+subax.xaxis.get_major_ticks():
		tick.label.set_backgroundcolor('w')
	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)
	return(subax)

def plot_bar(ax,x,to_plot,color):
	ax.fill_between([x-0.1,x+0.1],[np.nanmin(to_plot,axis=0),np.nanmin(to_plot,axis=0)],[np.nanmax(to_plot,axis=0),np.nanmax(to_plot,axis=0)],color=color,alpha=0.4)
	ax.plot([x-0.1,x+0.1],[np.nanmean(to_plot,axis=0),np.nanmean(to_plot,axis=0)],color='k')

def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None):
	season=all_regs[region][arg1]
	print('________'+region+'________')
	for scenario,color in zip(['Plus15-Future','Plus20-Future'],['orange','red']):
		to_plot = (data['seasMean'][:,scenario,region] - data['seasMean'][:,'All-Hist',region])
		plot_bar(subax,1,to_plot,color)

		to_plot = (data['mean_temp'][:,scenario,region,'14'] - data['mean_temp'][:,'All-Hist',region,'14'] )
		plot_bar(subax,2,to_plot,color)



	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.05, 0.05), xycoords='axes fraction', color=lb_color, weight='bold', fontsize=10)

fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[164,9], \
	arg1='summer',
	arg2=['pr'],
	arg3=['5mm'],
	arg4=['#FF3030'],
	title='temperature changes in JJA')
plt.savefig('plots/paper/Figure_summer.png',dpi=600)
