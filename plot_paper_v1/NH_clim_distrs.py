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



NH_regs={'ALA':{'color':'darkgreen','pos_off':(+10,+7),'summer':'JJA','winter':'DJF'},
		'WNA':{'color':'darkblue','pos_off':(+20,+15),'summer':'JJA','winter':'DJF'},
		'CNA':{'color':'gray','pos_off':(+8,-4),'summer':'JJA','winter':'DJF'},
		'ENA':{'color':'darkgreen','pos_off':(+18,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},
		# 'CAM':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'color':'darkgreen','pos_off':(-13,+0),'summer':'JJA','winter':'DJF'},
		'CEU':{'color':'darkblue','pos_off':(+9,+5),'summer':'JJA','winter':'DJF'},
		'CAS':{'color':'darkgreen','pos_off':(-8,+10),'summer':'JJA','winter':'DJF'},
		'NAS':{'color':'gray','summer':'JJA','winter':'DJF'},
		'TIB':{'color':'darkcyan','pos_off':(+2,-4),'summer':'JJA','winter':'DJF'},
		'EAS':{'color':'darkgreen','summer':'JJA','winter':'DJF'},

		'MED':{'color':'gray','pos_off':(-15,-5),'summer':'JJA','winter':'DJF'},
		'WAS':{'color':'darkcyan','pos_off':(-5,-5),'summer':'JJA','winter':'DJF'},
		'mid-lat':{'edge':'darkgreen','color':'none','alpha':1,'pos':(-142,35),'xlabel':'Period length [days]','ylabel':'Exceedence probability [%]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1.3}}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

#colors=['black']+sns.color_palette("colorblind", 4)




# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.axis('off')
	legend_elements=[]
	legend_elements.append(Line2D([0], [0], color='w', label='HadGHCND'))
	legend_elements.append(Line2D([0], [0], color='w', linestyle='--', label='EOBS'))
	legend_elements.append(Patch(facecolor='w', alpha=0.3, label='HAPPI models'))
	for style,state,color in zip(arg2,arg3,arg4):
		# legend_elements.append(Line2D([0], [0], color='w', label=state))
		if state == 'warm':
			legend_elements.append(Line2D([0], [0], color=color, label=' '))
		else:
			legend_elements.append(Line2D([0], [0], color='w', label=' '))
		legend_elements.append(Line2D([0], [0], color=color, linestyle='--', label=' '))
		legend_elements.append(Patch(facecolor=color,alpha=0.3, label=' '))


	subax.legend(handles=legend_elements ,title='                                   '+'      '.join([legend_dict[aa]+''.join([' ']*int(6/len(aa))) for aa in arg3]), loc='lower right',fontsize=9,ncol=len(arg3)+1, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)





def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	season=all_regs[region][arg1]
	print('________'+region+'________')
	for style,state,color in zip(arg2,arg3,arg4):
		ensemble=np.zeros([4,35])*np.nan
		nmax=35
		for dataset,i in zip(['MIROC5','ECHAM6-3-LR','CAM4-2degree','NorESM1'],range(4)):
			tmp_h=big_dict[dataset][region]['All-Hist'][state][season]
			count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) * 100 for ii in range(len(tmp_h['count']))])
			nmax=min(nmax,len(count_h))
			ensemble[i,:nmax]=count_h[0:nmax]
		#subax.plot(range(1,nmax+1),np.nanmean(ensemble[:,0:nmax],axis=0),color=color,linestyle=':')
		subax.fill_between(range(1,nmax+1),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=color,alpha=0.4,edgecolor=color)

		# if state=='warm':
		# 	#print(style,state)
		# 	print('HAPPI',np.nanmean(ensemble[:,21],axis=0))
		# 	#print('HAPPI',np.nanargmin(abs(np.nanmean(ensemble[:,:],axis=0)-1)))

	for style,state,color in zip(arg2,arg3,arg4):
		if region in ['CEU','NEU','MED']:
			tmp_h=big_dict['EOBS'][region]['All-Hist'][state][season]
			count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) * 100 for ii in range(len(tmp_h['count']))])
			subax.plot(range(1,len(count_h)+1),count_h,color=color,linestyle='--')
			if state=='warm':
				#print('EOBS',style,state)
				print('EOBS',count_h[21])
				#print('EOBS',np.nanargmin(abs(count_h-1)))

	if 'warm' in arg3:
		tmp_h=big_dict['HadGHCND'][region]['All-Hist']['warm'][season]
		count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) * 100 for ii in range(len(tmp_h['count']))])
		subax.plot(range(1,len(count_h)+1),count_h,color=arg4[0])
		print('HadGHCND',count_h[[7,14,21]])
		#print('HadGHCND',np.nanargmin(abs(count_h-1)))

		if region == 'mid-lat' and False:
			tau = -1/np.log(0.5)
			per_prob = np.exp(-1/tau*np.array(range(30),dtype=np.float)) *100
			per_count = per_prob / per_prob[-1]
			exceed_prob=np.array([np.sum(per_count[ii:])/float(np.sum(per_count)) * 100 for ii in range(len(per_count))])
			subax.plot(range(1,41),exceed_prob,'k--')

	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.95, 0.80), xycoords='axes fraction', color='black', weight='bold', fontsize=10, horizontalalignment='right')

def axis_settings(subax,label=False,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.set_yscale('log')
	subax.set_xlim((0,35))
	subax.set_ylim((0.01,100))
	subax.set_xticks([7,14,21,28,35])
	subax.tick_params(axis='x',which='both',bottom=True,top=True,labelbottom=label,labelsize=8)
	subax.set_yticks([0.01,0.1,1,10,100])
	subax.tick_params(axis='y',which='both',left=True,right=True,labelleft=label,labelsize=8)
	locmin = mticker.LogLocator(base=10, subs=[1.0])
	subax.yaxis.set_minor_locator(locmin)
	subax.yaxis.set_minor_formatter(mticker.NullFormatter())
	subax.yaxis.get_label().set_backgroundcolor('w')
	for tick in subax.yaxis.get_major_ticks():
		tick.label.set_backgroundcolor('w')
	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)

	return(subax)

plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rain'}

fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[164,9], \
	arg1='summer',
	arg2=['tas','pr','cpd','pr'],
	arg3=['warm','dry','dry-warm','5mm'],
	arg4=['#FF3030','#FF8C00','#BF3EFF','#009ACD'],
	title=None)

plt.annotate('d', xy=(0.03, 0.93), xycoords='figure fraction', fontsize=15,fontweight='bold', backgroundcolor='w')
plt.savefig('plots/paper/NH_clim_distrs.png',dpi=600)
#
#
# def axis_settings(subax,label=False,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
# 	subax.set_yscale('log')
# 	subax.set_xlim((0,21))
# 	subax.set_ylim((0.01,100))
# 	subax.set_xticks([7,14,21])
# 	subax.tick_params(axis='x',which='both',bottom=True,top=True,labelbottom=label,labelsize=8)
# 	subax.set_yticks([0.01,0.1,1,10,100])
# 	subax.tick_params(axis='y',which='both',left=True,right=True,labelleft=label,labelsize=8)
# 	locmin = mticker.LogLocator(base=10, subs=[1.0])
# 	subax.yaxis.set_minor_locator(locmin)
# 	subax.yaxis.set_minor_formatter(mticker.NullFormatter())
# 	subax.yaxis.get_label().set_backgroundcolor('w')
# 	for tick in subax.yaxis.get_major_ticks():
# 		tick.label.set_backgroundcolor('w')
# 	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)
#
# 	return(subax)
#
# fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[164,9], \
# 	arg1='summer',
# 	arg2=['pr','pr'],
# 	arg3=['5mm','10mm'],
# 	arg4=['cyan','blue'],
# 	title='exceedance probabilites of persistence in JJA')
# plt.savefig('plots/paper/NH_clim_distrs_wet.png',dpi=600)
