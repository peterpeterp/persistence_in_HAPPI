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

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker

import seaborn as sns
sns.set_style("whitegrid")


try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

sys.path.append('/Users/peterpfleiderer/Projects/git-packages/regional_panels_on_map')
import regional_panels_on_map as regional_panels_on_map; reload(regional_panels_on_map)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

os.chdir('persistence_in_HAPPI/plot_paper')
import __plot_imports; reload(__plot_imports); from __plot_imports import *
os.chdir('../../')



pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

if 'big_dict' not in globals():
	big_dict={}
	for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree','EOBS','HadGHCND']:
		infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
		pkl_file=open(infile, 'rb')
		big_dict[dataset] = pickle.load(pkl_file);	pkl_file.close()

all_regs=NH_regs.copy()
all_regs['mid-lat']['pos']=(-142,27)

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

#colors=['black']+sns.color_palette("colorblind", 4)



def distrs(subax,region,info_dict):
	for state,details in info_dict.items():
		ensemble=np.zeros([4,35])*np.nan
		nmax=21
		for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
			tmp_20=big_dict[dataset][region]['Plus20-Future'][state]['JJA']
			tmp_h=big_dict[dataset][region]['All-Hist'][state]['JJA']
			count_20=np.array([np.sum(tmp_20['count'][ii:])/float(np.sum(tmp_20['count'])) for ii in range(len(tmp_20['count']))])
			count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) for ii in range(len(tmp_h['count']))])
			nmax=min(len(count_20),len(count_h),nmax)
			tmp=(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100
			ensemble[i,:nmax]=tmp

		if state != '5mm':
			subax.plot(range(details['shift'],nmax+details['shift']),np.nanmean(ensemble[:,0:nmax],axis=0),color=details['color'],linestyle='-')
			subax.fill_between(range(details['shift'],nmax+details['shift']),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=details['color'], edgecolor=details['color'],alpha=0.3)
		if state == '5mm':
			subax2 = subax.twinx()
			subax2.set_zorder(3)
			subax2.set_ylim((-75,100))
			subax2.grid(False)
			subax2.tick_params(axis='y',which='both',left=True,right=True,labelright=False,labelsize=8)
			subax2.plot(range(details['shift'],nmax+details['shift']),np.nanmean(ensemble[:,0:nmax],axis=0),color=details['color'],linestyle='-',zorder=3)
			subax2.fill_between(range(details['shift'],nmax+details['shift']),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=details['color'],alpha=0.3,edgecolor=details['color'])
			if region == 'mid-lat':
				subax2.yaxis.tick_right()
				subax2.set_ylabel('for rain persistence',fontsize=8, color=details['color'])
				subax2.tick_params(axis='y',which='both',left=True,right=True,labelright=True,labelsize=8, colors=details['color'])
				subax2.locator_params(axis = 'y', nbins = 8)
				subax2.yaxis.get_label().set_backgroundcolor('w')
				bbox = dict(boxstyle="round", ec="w", fc="w", alpha=1)
				plt.setp(subax2.get_yticklabels(), bbox=bbox)
				for pos in ['top', 'bottom', 'right', 'left']:
					subax2.spines[pos].set_edgecolor(NH_regs[region]['edge'])

	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.04, 0.07), xycoords='axes fraction', color='black', weight='bold', fontsize=8,backgroundcolor='w')

def axis_settings(subax,info_dict,label=False,region=None):
	subax.set_xlim((0,84))
	subax.set_ylim((-15,20))
	subax.plot([0,84],[0,0],'k')
	subax.set_xticks(np.arange(7,86,7))
	for x in [21,42,63,84]:
		subax.axvline(x,color='k')
	if region == 'mid-lat':
		subax.set_xticklabels(['7','14','','7','14','','7','14','','7','14',''])
		subax.set_xlabel('Period length [days]',fontsize=8)
		subax.set_ylabel('rel. change in\nExceedence probability [%]',fontsize=8)
		subax.tick_params(axis='x',labelsize=8, colors='k',size=1)
		subax.tick_params(axis='y',labelsize=8, colors='k',size=1)
		subax.yaxis.get_label().set_backgroundcolor('w')
		bbox = dict(boxstyle="round", ec="w", fc="w", alpha=1)
		plt.setp(subax.get_yticklabels(), bbox=bbox)
	else:
		subax.set_yticklabels([])
		subax.set_xticklabels([])
	subax.locator_params(axis = 'y', nbins = 8)
	subax.grid(True,which="both",ls="--",c='gray',lw=0.35)
	return(subax)

plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rain'}

info_dict = {
	'warm': {
		'state':'warm', 'name':'warm', 'style':'tas', 'color':'#FF3030', 'c_range':(-15,20), 'letter':'a', 'shift':0,
	},
	'dry': {
		'state':'dry', 'name':'dry', 'style':'pr', 'color':'#FF8C00', 'c_range':(-15,20), 'letter':'b', 'shift':21,
	},
	'dry-warm': {
		'state':'dry-warm', 'name':'dry-warm', 'style':'cpd', 'color':'#BF3EFF', 'c_range':(-15,20), 'letter':'c', 'shift':42,
	},
	'5mm': {
		'state':'5mm', 'name':'rain', 'style':'pr', 'color':'#009ACD', 'c_range':(-50,100), 'letter':'d', 'shift':63,
	}
}

plt.close('all')
fig,ax_map=regional_panels_on_map.regional_panels_on_map(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.1, info_dict = info_dict, title=None)

ax_panels=fig.add_axes([0,0,1,1], zorder=0)
ax_panels.axis('off')
ax_panels.set_xlim(0,1)
ax_panels.set_ylim(0,1)
ax_panels.fill_between([0,0.2],[0,0],[0.6,0.6],color='w', zorder=0)

# ax_map.annotate(info_dict['letter'], xy=(0.01, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=13)
legax = fig.add_axes([0.85,0.05,0.145,0.9], zorder=4)
legax.axis('off')
legend_elements=[]

legend_elements.append(Line2D([0], [0], color='w', linestyle='-', label='ensemble mean'))
for state,details in info_dict.items():
	legend_elements.append(Line2D([0], [0], color=details['color'], linestyle='-', label=state))

legend_elements.append(Patch(facecolor='w',alpha=0.3, label=' '))
legend_elements.append(Patch(facecolor='w',alpha=0.3, label='model spread'))
for state,details in info_dict.items():
	legend_elements.append(Patch(facecolor=details['color'],alpha=0.3, label=state))

legax.legend(handles=legend_elements , loc='upper right',fontsize=8,ncol=1, frameon=True, facecolor='w', framealpha=1, edgecolor='w')

plt.tight_layout(); plt.savefig('plots/poster/NH_changes_'+'-'.join([str(tt) for tt in info_dict.keys()])+'.png',dpi=600, transparent=True)









#
