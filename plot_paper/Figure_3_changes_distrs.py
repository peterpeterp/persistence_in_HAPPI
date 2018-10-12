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
	for style in ['tas','pr','cpd']:
		big_dict[style]={}
		for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree','HadGHCND','EOBS']:
			infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
			if os.path.isfile(infile):
				pkl_file=open(infile, 'rb')
				big_dict[style][dataset] = pickle.load(pkl_file);	pkl_file.close()
			infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_mid-lat.pkl'
			if os.path.isfile(infile):
				pkl_file=open(infile, 'rb')
				big_dict[style][dataset]['NHml'] = pickle.load(pkl_file)['mid-lat'];	pkl_file.close()

			infile = 'data/'+dataset+'/'+style+'_'+dataset+'_regional_distrs_srex.pkl'
			if os.path.isfile(infile):
				pkl_file=open(infile, 'rb')
				big_dict[style][dataset] = pickle.load(pkl_file);	pkl_file.close()
			infile = 'data/'+dataset+'/'+style+'_'+dataset+'_regional_distrs_mid-lat.pkl'
			if os.path.isfile(infile):
				pkl_file=open(infile, 'rb')
				big_dict[style][dataset]['NHml'] = pickle.load(pkl_file)['mid-lat'];	pkl_file.close()

NH_regs={'ALA':{'color':'darkgreen','pos_off':(+10,+7),'summer':'JJA','winter':'DJF'},
		'WNA':{'color':'darkblue','pos_off':(+20,+15),'summer':'JJA','winter':'DJF'},
		'CNA':{'color':'gray','pos_off':(+8,-4),'summer':'JJA','winter':'DJF'},
		'ENA':{'color':'darkgreen','pos_off':(+18,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},
		'CAM':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'color':'darkgreen','pos_off':(-13,+0),'summer':'JJA','winter':'DJF'},
		'CEU':{'color':'darkblue','pos_off':(+10,+5),'summer':'JJA','winter':'DJF'},
		'CAS':{'color':'darkgreen','pos_off':(+0,+10),'summer':'JJA','winter':'DJF'},
		'NAS':{'color':'gray','summer':'JJA','winter':'DJF'},
		'TIB':{'color':'darkcyan','pos_off':(+0,-14),'summer':'JJA','winter':'DJF'},
		'EAS':{'color':'darkgreen','summer':'JJA','winter':'DJF'},

		'MED':{'color':'gray','pos_off':(-15,-5),'summer':'JJA','winter':'DJF'},
		'WAS':{'color':'darkcyan','pos_off':(-5,-5),'summer':'JJA','winter':'DJF'},
		'NHml':{'edge':'darkblue','color':'none','alpha':1,'pos':(-142,28),'xlabel':'period length [days]','ylabel':'exceedence probability [%]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1.3}}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['NHml']={'points':[(-180,23),(180,23),(180,66),(-180,66)]}

colors=['black']+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None):
	subax.axis('off')
	# for style,state,color in zip(arg2,arg3,arg4):
	# 	subax.fill_between([1,1],[1,1],[1,1],label=state+' ensemble spread',facecolor=color,alpha=0.3)
	# 	# subax.plot([1,1],[1,1],label='ensemble mean',color=color)
	# 	subax.plot([1,1],[1,1],label=state+' HadGHCND',color=color)
	# 	subax.plot([1,1],[1,1],label=state+' EOBS',color=color,linestyle='--')
	# legend = subax.legend(loc='lower right',fontsize=9,ncol=3, frameon=True, facecolor='w', framealpha=1, edgecolor='w')

	legend_elements=[]
	# legend_elements.append(Line2D([0], [0], color='w', label=' '))
	#legend_elements.append(Line2D([0], [0], color='w', label='HadGHCND'))
	legend_elements.append(Line2D([0], [0], color='w', linestyle='--', label='Ensemble Median'))
	legend_elements.append(Patch(facecolor='w', alpha=0.3, label='Model Spread'))
	for style,state,color in zip(arg2,arg3,arg4):
		# legend_elements.append(Line2D([0], [0], color='w', label=state))
		#legend_elements.append(Line2D([0], [0], color=color, label=' '))
		legend_elements.append(Line2D([0], [0], color=color, linestyle='--', label=' '))
		legend_elements.append(Patch(facecolor=color,alpha=0.3, label=' '))


	subax.legend(handles=legend_elements ,title='                                     '+arg3[0]+'        '+arg3[1]+'       '+arg3[2] ,loc='lower right',fontsize=9,ncol=4, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)


def axis_settings(subax,label='off',arg1=None,arg2=None,arg3=None,arg4=None):
	subax.set_xlim((0,35))
	subax.set_ylim((-40,40))
	subax.plot([0,35],[0,0],'k')
	subax.set_xticks([7,14,21,28,35])
	subax.tick_params(axis='x',which='both',bottom=True,top=True,labelbottom=label,labelsize=8)
	subax.tick_params(axis='y',which='both',left=True,right=True,labelleft=label,labelsize=8)
	subax.locator_params(axis = 'y', nbins = 5)
	subax.locator_params(axis = 'x', nbins = 5)
	subax.yaxis.get_label().set_backgroundcolor('w')
	for tick in subax.yaxis.get_major_ticks():
		tick.label.set_backgroundcolor('w')
	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)
	return(subax)

def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None):
	season=all_regs[region][arg1]
	for style,state,color in zip(arg2,arg3,arg4):
		ensemble=np.zeros([4,35])*np.nan
		nmax=35
		for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
			tmp_20=big_dict[style][dataset][region]['Plus20-Future'][season][state]
			tmp_h=big_dict[style][dataset][region]['All-Hist'][season][state]
			count_20=np.array([np.sum(tmp_20['count'][ii:])/float(np.sum(tmp_20['count'])) for ii in range(len(tmp_20['count']))])
			count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) for ii in range(len(tmp_h['count']))])
			nmax=min(len(count_20),len(count_h),nmax)
			tmp=(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100
			ensemble[i,:nmax]=tmp
		subax.plot(range(1,nmax+1),np.nanmean(ensemble[:,0:nmax],axis=0),color=color,linestyle=':')
		subax.fill_between(range(1,nmax+1),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=color,alpha=0.3)

	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.05, 0.05), xycoords='axes fraction', color=lb_color, weight='bold', fontsize=10)


fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[164,9], \
	arg1='summer',
	arg2=['tas','pr','cpd'],
	arg3=['warm','dry','dry-warm'],
	arg4=['#FF3030','#FF8C00','#8B3A62'],
	title='rel. change in exceedance probabilites in JJA')
plt.savefig('plots/paper/Figure2_a.png',dpi=600)

# fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[30,9], \
# 	arg1='summer', arg2=['tas','pr','cpd'], arg3=['warm','dry','dry-warm'], arg4=sns.color_palette("hls", 3), title='rel. change in exceedance probabilites in JJA')
# plt.savefig('plots/paper/Figure2_a.png',dpi=600)
#
# fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[30,9], \
# 	arg1='summer', arg2=['tas','pr','cpd'], arg3=['cold','wet','wet-cold'], arg4=sns.color_palette("hls", 3), title='rel. change in exceedance probabilites in JJA')
# plt.savefig('plots/paper/Figure2_b.png',dpi=600)
#
#
# fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[30,9], \
# 	arg1='winter', arg2=['tas','pr','cpd'], arg3=['warm','dry','dry-warm'], arg4=sns.color_palette("hls", 3), title='rel. change in exceedance probabilites in DJF')
# plt.savefig('plots/paper/Figure2_a_DJF.png',dpi=600)
#
# fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[30,9], \
# 	arg1='winter', arg2=['tas','pr','cpd'], arg3=['cold','wet','wet-cold'], arg4=sns.color_palette("hls", 3), title='rel. change in exceedance probabilites in DJF')
# plt.savefig('plots/paper/Figure2_b_DJF.png',dpi=600)
