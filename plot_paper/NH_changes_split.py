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


sys.path.append('/Users/peterpfleiderer/Projects/allgemeine_scripte')
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

if 'big_dict' not in globals():
	big_dict={}
	for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree','EOBS','HadGHCND']:
		infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
		pkl_file=open(infile, 'rb')
		big_dict[dataset] = pickle.load(pkl_file);	pkl_file.close()

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

#colors=['black']+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.axis('off')

def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	season=all_regs[region][arg1]
	for style,state,color,shift in zip(arg2[::-1],arg3[::-1],arg4[::-1],arg5[::-1]):
		ensemble=np.zeros([4,35])*np.nan
		nmax=21
		for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
			tmp_20=big_dict[dataset][region]['Plus20-Future'][state][season]
			tmp_h=big_dict[dataset][region]['All-Hist'][state][season]
			count_20=np.array([np.sum(tmp_20['count'][ii:])/float(np.sum(tmp_20['count'])) for ii in range(len(tmp_20['count']))])
			count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) for ii in range(len(tmp_h['count']))])
			nmax=min(len(count_20),len(count_h),nmax)
			tmp=(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100
			ensemble[i,:nmax]=tmp

		if state != '5mm':
			subax.plot(range(shift,nmax+shift),np.nanmean(ensemble[:,0:nmax],axis=0),color=color,linestyle='-')
			subax.fill_between(range(shift,nmax+shift),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=color, edgecolor=color,alpha=0.3)
		if state == '5mm':
			global subax2
			subax2 = subax.twinx()
			subax2.set_ylim((-75,100))
			subax2.grid(False)
			subax2.tick_params(axis='y',which='both',left=True,right=True,labelright=False,labelsize=8)
			subax2.plot(range(shift,nmax+shift),np.nanmean(ensemble[:,0:nmax],axis=0),color=color,linestyle='-')
			subax2.fill_between(range(shift,nmax+shift),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=color,alpha=0.3,edgecolor=color)
			if region == 'mid-lat':
				subax2.yaxis.tick_right()
				subax2.set_ylabel('for rain persistence',fontsize=8, color=color)
				subax2.tick_params(axis='y',which='both',left=True,right=True,labelright=True,labelsize=8, colors=color)
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

def axis_settings(subax,label=False,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None,region=None):
	subax.set_xlim((0,84))
	subax.set_ylim(c_range)
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

plt.close('all')
arg2 = ['tas','pr','cpd','pr']
arg3 = ['warm','dry','dry-warm','5mm']
arg4 = ['#FF3030','#FF8C00','#BF3EFF','#009ACD']
arg5 = [1,22,43,64]
c_range = [(-15,20),(-15,20),(-15,20),(-50,100)]
for combi in [[0,1,2,3]]:
	arg2_,arg3_,arg4_,arg5_ = [],[],[],[]
	for aa,aa_all in zip([arg2_,arg3_,arg4_,arg5_],[arg2,arg3,arg4,arg5]):
		for co in combi:
			aa.append(aa_all[co])
	if combi != [3]:
		c_range = (-15,20)
	else:
		c_range = (-50,100)
	fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.1, legend_plot=legend_plot, legend_pos=[164,9], \
		arg1='summer',
		arg2=arg2_,
		arg3=arg3_,
		arg4=arg4_,
		arg5=arg5_,
		title=None)

	with sns.axes_style("white"):
		legax = fig.add_axes([0.89,0.01,0.105,0.98], facecolor='w')
	plt.setp(legax.spines.values(), color='k', linewidth=2)
	legax.set_yticklabels([])
	legax.set_xticklabels([])

	legend_elements=[]

	legend_elements.append(Line2D([0], [0], color='w', label='model spread'))
	for style,state,color in zip(arg2,arg3,arg4):
		legend_elements.append(Patch(facecolor=color,alpha=0.3, label=state))

	legend_elements.append(Line2D([0], [0], color='w', label=''))
	legend_elements.append(Line2D([0], [0], color='w', label='ensemble\nmean'))
	for style,state,color in zip(arg2,arg3,arg4):
		legend_elements.append(Line2D([0], [0], color=color, linestyle='-', label=state))

	legax.legend(handles=legend_elements, loc='upper right',fontsize=9,ncol=1, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)

	plt.tight_layout(); plt.savefig('plots/NH_clim_distrs_'+'-'.join([str(tt) for tt in arg3])+'.png',dpi=600); plt.close()









#
