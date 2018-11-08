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

if 'big_dict' not in globals():
	big_dict={}
	for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
		infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
		pkl_file=open(infile, 'rb')
		big_dict[dataset] = pickle.load(pkl_file);	pkl_file.close()

NH_regs={'ALA':{'color':'darkgreen','pos_off':(+10,+7),'summer':'JJA','winter':'DJF'},
		'WNA':{'color':'darkblue','pos_off':(+20,+15),'summer':'JJA','winter':'DJF'},
		'CNA':{'color':'gray','pos_off':(+8,-4),'summer':'JJA','winter':'DJF'},
		'ENA':{'color':'darkgreen','pos_off':(+18,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},
		'CAM':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'color':'darkgreen','pos_off':(-13,+0),'summer':'JJA','winter':'DJF'},
		'CEU':{'color':'darkblue','pos_off':(+9,+5),'summer':'JJA','winter':'DJF'},
		'CAS':{'color':'darkgreen','pos_off':(-8,+14),'summer':'JJA','winter':'DJF'},
		'NAS':{'color':'gray','summer':'JJA','winter':'DJF'},
		'TIB':{'color':'darkcyan','pos_off':(+2,-4),'summer':'JJA','winter':'DJF'},
		'EAS':{'color':'darkgreen','summer':'JJA','winter':'DJF'},

		'MED':{'color':'gray','pos_off':(-15,-5),'summer':'JJA','winter':'DJF'},
		'WAS':{'color':'darkcyan','pos_off':(-5,-1),'summer':'JJA','winter':'DJF'},
		'mid-lat':{'edge':'darkgreen','color':'none','alpha':1,'pos':(-142,40),'xlabel':'','ylabel':'rel. change in exceedence probability\nfor periods longer than 2 weeks [%]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1.3}}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

colors=['black']+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None):
	subax.axis('off')
	legend_elements=[]
	legend_elements.append(Line2D([0], [0], color='w', linestyle='--', label='+1.5$^\circ$C Ensemble Median'))
	legend_elements.append(Line2D([0], [0], color='w', linestyle='--', label='+2.0$^\circ$CEnsemble Median'))
	legend_elements.append(Patch(facecolor='w', alpha=0.3, label='Model Spread'))
	for style,state,color in zip(arg2,arg3,arg4):
		for scenario,hatch,marker,shift in zip(['Plus15-Future','Plus20-Future'],['---','///'],['x','+'],[-0.2,0.2]):
			legend_elements.append(Line2D([0], [0], color='k', linestyle='', label=' ', marker=marker))
		legend_elements.append(Patch(facecolor=color,alpha=0.4, label=' '))

	subax.legend(handles=legend_elements ,title='                                              '+'    '.join([aa+''.join([' ']*int(6/len(aa))) for aa in arg3]), loc='lower right',fontsize=9,ncol=len(arg3)+1, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)



def axis_settings(subax,label=False,arg1=None,arg2=None,arg3=None,arg4=None):
	subax.set_xlim((0.5,len(arg3)+0.5))
	subax.set_ylim((-30,30))
	subax.set_xticks(range(1,len(arg3)+1))
	subax.set_xticklabels([a3+'\n'+str(a2)+'-day periods' for a3,a2 in zip(arg3,arg2)])
	subax.tick_params(axis='x',which='both',bottom=True,top=True,labelbottom=label,labelsize=7,rotation=90)
	subax.set_yticks([-20,-10,0,10,20])
	subax.tick_params(axis='y',which='both',left=True,right=True,labelleft=label,labelsize=7)
	subax.yaxis.get_label().set_backgroundcolor('w')
	for tick in subax.yaxis.get_major_ticks()+subax.xaxis.get_major_ticks():
		tick.label.set_backgroundcolor('w')
	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)
	subax.axhline(y=0,c='gray')
	return(subax)

def plot_bar(ax,x,to_plot,color,hatch=None, alpha=0.4, marker='+'):
	ax.fill_between([x-0.1,x+0.1],[np.nanmin(to_plot,axis=0),np.nanmin(to_plot,axis=0)],[np.nanmax(to_plot,axis=0),np.nanmax(to_plot,axis=0)],\
	 color=color, edgecolor='k', hatch=hatch, alpha=alpha)
	#ax.plot([x-0.1,x+0.1],[np.nanmean(to_plot,axis=0),np.nanmean(to_plot,axis=0)],color='k')
	ax.scatter([x],[np.nanmean(to_plot,axis=0)],color='k',marker=marker)



def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None):
	season=all_regs[region][arg1]
	print('________'+region+'________')
	for state,per_length,color,pos in zip(arg3,arg2,arg4,range(1,1+len(arg3))):
		for scenario,hatch,marker,shift in zip(['Plus15-Future','Plus20-Future'],['---','///'],['x','+'],[-0.2,0.2]):
			ensemble=np.zeros([4])*np.nan
			nmax=35
			for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
				tmp_fu=big_dict[dataset][region][scenario][state][season]
				tmp_h=big_dict[dataset][region]['All-Hist'][state][season]
				count_fu=np.sum(tmp_fu['count'][per_length:])/float(np.sum(tmp_fu['count']))
				count_h=np.sum(tmp_h['count'][per_length:])/float(np.sum(tmp_h['count']))
				ensemble[i]= (count_fu - count_h) / count_h * 100.

			plot_bar(subax,pos+shift,ensemble,color,hatch=hatch,marker=marker)


	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.05, 0.05), xycoords='axes fraction', color='k', weight='bold', fontsize=10)

fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[164,9], \
	arg1='summer',
	arg2=[14,14,14,3,3],
	arg3=['warm','dry','dry-warm','5mm','10mm'],
	arg4=['#FF3030','#FF8C00','#8B3A62','cyan','blue'],
	title='rel. change in exceedance probabilites of persistence in JJA')
plt.savefig('plots/paper/NH_summary.png',dpi=600)
