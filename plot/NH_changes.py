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

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

#colors=['black']+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.axis('off')
	legend_elements=[]
	# legend_elements.append(Line2D([0], [0], color='w', label=' '))
	#legend_elements.append(Line2D([0], [0], color='w', label='HadGHCND'))
	legend_elements.append(Line2D([0], [0], color='w', linestyle='--', label='ensemble mean'))
	legend_elements.append(Patch(facecolor='w', alpha=0.3, label='model spread'))
	for style,state,color in zip(arg2,arg3,arg4):
		# legend_elements.append(Line2D([0], [0], color='w', label=state))
		#legend_elements.append(Line2D([0], [0], color=color, label=' '))
		legend_elements.append(Line2D([0], [0], color=color, linestyle='-', label=' '))
		legend_elements.append(Patch(facecolor=color,alpha=0.3, label=' '))


	subax.legend(handles=legend_elements ,title='                                       '+'      '.join([legend_dict[aa]+''.join([' ']*int(6/len(aa))) for aa in arg3]), loc='lower right',fontsize=9,ncol=len(arg3)+1, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)

def distrs(subax,region,info_dict):
	ensemble=np.zeros([4,35])*np.nan
	nmax=35
	for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
		tmp_20=big_dict[dataset][region]['Plus20-Future'][info_dict['state']]['JJA']
		tmp_h=big_dict[dataset][region]['All-Hist'][info_dict['state']]['JJA']
		count_20=np.array([np.sum(tmp_20['count'][ii:])/float(np.sum(tmp_20['count'])) for ii in range(len(tmp_20['count']))])
		count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) for ii in range(len(tmp_h['count']))])
		nmax=min(len(count_20),len(count_h),nmax)
		tmp=(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100
		ensemble[i,:nmax]=tmp

	subax.plot(range(1,nmax+1),np.nanmean(ensemble[:,0:nmax],axis=0),color=info_dict['color'],linestyle='-')
	subax.fill_between(range(1,nmax+1),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=info_dict['color'], edgecolor=info_dict['color'],alpha=0.3)

	# print('%s\t%0.2f (%0.2f to %0.2f)\t%0.2f (%0.2f to %0.2f)\t%0.2f (%0.2f to %0.2f)' %(region, np.nanmean(ensemble[:,7],axis=0), np.nanmin(ensemble[:,7],axis=0), np.nanmax(ensemble[:,7],axis=0), np.nanmean(ensemble[:,14],axis=0), np.nanmin(ensemble[:,14],axis=0), np.nanmax(ensemble[:,14],axis=0), np.nanmean(ensemble[:,21],axis=0), np.nanmin(ensemble[:,21],axis=0), np.nanmax(ensemble[:,21],axis=0)))
	print('%s\t%0.2f (%0.2f, %0.2f, %0.2f, %0.2f)\t%0.2f (%0.2f, %0.2f, %0.2f, %0.2f)\t%0.2f (%0.2f, %0.2f, %0.2f, %0.2f)' %(region, np.nanmean(ensemble[:,7],axis=0), np.sort(ensemble[:,7])[0], np.sort(ensemble[:,7])[1], np.sort(ensemble[:,7])[2], np.sort(ensemble[:,7])[3], np.nanmean(ensemble[:,14],axis=0), np.sort(ensemble[:,14])[0], np.sort(ensemble[:,14])[1], np.sort(ensemble[:,14])[2], np.sort(ensemble[:,14])[3], np.nanmean(ensemble[:,21],axis=0), np.sort(ensemble[:,21])[0], np.sort(ensemble[:,21])[1], np.sort(ensemble[:,21])[2], np.sort(ensemble[:,21])[3]))

	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.05, 0.05), xycoords='axes fraction', color='black', weight='bold', fontsize=10)

def axis_settings(subax,info_dict,label=False,region=None):
	subax.set_xlim((0,35))
	subax.set_ylim(info_dict['c_range'])
	subax.plot([0,35],[0,0],'k')
	subax.set_xticks(np.arange(7,42,7))
	if region == 'mid-lat':
		subax.set_xticklabels(['7','14','21','35'])
		subax.set_xlabel('Period length [days]',fontsize=10)
		subax.set_ylabel('rel. change in\nExceedence probability [%]',fontsize=10)
		subax.tick_params(axis='x',labelsize=10, colors='k',size=1)
		subax.tick_params(axis='y',labelsize=10, colors='k',size=1)
		subax.yaxis.get_label().set_backgroundcolor('w')
		bbox = dict(boxstyle="round", ec="w", fc="w", alpha=1)
		plt.setp(subax.get_yticklabels(), bbox=bbox)
	else:
		subax.set_yticklabels([])
		subax.set_xticklabels([])
	subax.locator_params(axis = 'y', nbins = 5)
	subax.grid(True,which="both",ls="--",c='gray',lw=0.35)
	return(subax)

plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"


info_dicts = {
	'warm': {
		'state':'warm', 'name':'warm', 'style':'tas', 'color':'#FF3030', 'c_range':(-15,20), 'letter':'a'
	},
	'dry': {
		'state':'dry', 'name':'dry', 'style':'pr', 'color':'#FF8C00', 'c_range':(-15,20), 'letter':'b'
	},
	'dry-warm': {
		'state':'dry-warm', 'name':'dry-warm', 'style':'cpd', 'color':'#BF3EFF', 'c_range':(-15,20), 'letter':'c'
	},
	'5mm': {
		'state':'5mm', 'name':'rain', 'style':'pr', 'color':'#009ACD', 'c_range':(-50,100), 'letter':'d'
	}
}

for name,info_dict in info_dicts.items():
	print('Region\t7-day %s period\t14-day %s period\t21-day %s period' %(name,name,name))

	plt.close('all')
	fig,ax_map=regional_panels_on_map.regional_panels_on_map(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.1, info_dict = info_dict, title=None)

	ax_map.annotate(info_dict['letter'], xy=(0.01, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=13)


	legax = fig.add_axes([0.85,0.05,0.145,0.9])
	legax.axis('off')
	legend_elements=[]
	legend_elements.append(Line2D([0], [0], color=info_dict['color'], linestyle='-', label='ensemble mean'))
	legend_elements.append(Patch(facecolor=info_dict['color'],alpha=0.3, label='model spread'))

	legax.legend(handles=legend_elements ,title=info_dict['name']+' persistence', loc='upper right',fontsize=10,ncol=1, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)


	plt.tight_layout(); plt.savefig('plots/NH_changes_'+name+'.png',dpi=600); plt.close()




'''

Region	7-day rain period	14-day rain period	21-day rain period
ALA	17.33 (7.70, 8.21, 21.30, 32.12)	17.93 (-38.16, -11.79, 32.78, 88.91)	128.64 (-25.29, 282.58, nan, nan)
CAS	-7.43 (-16.62, -12.43, -4.98, 4.32)	-12.22 (-26.29, -22.69, -21.06, 21.17)	-20.28 (-42.57, 2.01, nan, nan)
CEU	17.65 (-0.14, 9.33, 27.10, 34.29)	43.76 (11.16, 14.34, 28.77, 120.79)	nan (nan, nan, nan, nan)
CGI	17.37 (3.04, 10.61, 25.97, 29.87)	58.62 (-26.15, 78.33, 90.22, 92.06)	nan (nan, nan, nan, nan)
CNA	8.14 (-3.47, 0.98, 17.28, 17.77)	-0.71 (-49.91, -4.69, 19.18, 32.57)	nan (nan, nan, nan, nan)
EAS	13.34 (4.47, 12.94, 13.04, 22.93)	16.79 (3.60, 10.37, 23.70, 29.49)	18.93 (3.49, 6.61, 32.71, 32.92)
ENA	11.28 (8.00, 8.85, 10.84, 17.44)	8.64 (-15.08, 11.28, 11.33, 27.03)	nan (nan, nan, nan, nan)
MED	5.33 (-2.66, 3.08, 8.50, 12.40)	nan (nan, nan, nan, nan)	nan (nan, nan, nan, nan)
NAS	38.63 (28.21, 35.68, 38.61, 52.03)	77.04 (14.23, 23.80, 95.15, 175.00)	nan (nan, nan, nan, nan)
NEU	25.73 (11.16, 15.54, 27.37, 48.84)	28.98 (-0.06, 20.55, 23.45, 71.99)	nan (nan, nan, nan, nan)
TIB	1.51 (-4.43, -2.15, 5.48, 7.15)	-0.91 (-5.86, -1.35, -1.01, 4.57)	-0.62 (-3.98, -0.39, 0.09, 1.80)
WAS	2.20 (-3.50, -2.15, 5.66, 8.79)	8.91 (-3.63, -0.40, 11.07, 28.59)	55.47 (-7.84, -4.22, 26.55, 207.38)
WNA	-5.51 (-13.92, -12.35, -1.90, 6.12)	-27.68 (-55.40, -52.71, -11.54, 8.93)	nan (nan, nan, nan, nan)
mid-lat	26.06 (15.24, 16.03, 36.15, 36.84)	52.88 (23.79, 33.17, 70.01, 84.56)	74.07 (-11.73, -7.24, 81.75, 233.51)

'''






#
