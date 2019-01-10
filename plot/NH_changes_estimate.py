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
from scipy.optimize import curve_fit

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

state_count = da.read_nc('data/state_count_srex.nc')['state_count']


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
		'mid-lat':{'edge':'darkgreen','color':'none','alpha':1,'pos':(-142,35),'xlabel':'period length [days]','ylabel':'exceedence probability [%]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1.3}}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

#colors=['black']+sns.color_palette("colorblind", 4)
legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rainy'}

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None):
	subax.axis('off')
	legend_elements=[]
	# legend_elements.append(Line2D([0], [0], color='w', label=' '))
	#legend_elements.append(Line2D([0], [0], color='w', label='HadGHCND'))
	legend_elements.append(Line2D([0], [0], color='w', linestyle='--', label='ensemble mean'))
	legend_elements.append(Patch(facecolor='w', alpha=0.3, label='model spread'))
	for style,state,color in zip(arg2,arg3,arg4):
		# legend_elements.append(Line2D([0], [0], color='w', label=state))
		#legend_elements.append(Line2D([0], [0], color=color, label=' '))
		legend_elements.append(Line2D([0], [0], color=color, linestyle='--', label=' '))
		legend_elements.append(Patch(facecolor=color,alpha=0.3, label=' '))

	legend_elements.append(Line2D([0], [0], color=arg1, linestyle='--', label=' '))
	legend_elements.append(Patch(facecolor=arg1,alpha=0.3, label=' '))

	subax.legend(handles=legend_elements ,title='                                       '+'      '.join([legend_dict[aa]+''.join([' ']*int(6/len(aa))) for aa in arg3]+['fit']), loc='lower right',fontsize=9,ncol=len(arg3)+2, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)


def func(x, a, b):
    return a * np.exp(-b * x)

def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None):
	season=all_regs[region]['summer']
	for style,state,color in zip(arg2,arg3,arg4):
		global ensemble,state_change
		ensemble=np.zeros([4,35])*np.nan
		ensemble_fit=np.zeros([4,35])*np.nan
		nmax=35
		state_change = []
		for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
			tmp_h=big_dict[dataset][region]['All-Hist'][state][season]
			prob_h=tmp_h['count']/float(np.nansum(tmp_h['count'])) * 100
			excee_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) * 100 for ii in range(len(tmp_h['count']))])
			nmax=min(nmax,np.where(excee_h>0)[0][-1])

			tmp_f=big_dict[dataset][region]['Plus20-Future'][state][season]
			prob_f=tmp_f['count']/float(np.nansum(tmp_f['count'])) * 100
			excee_f=np.array([np.sum(tmp_f['count'][ii:])/float(np.sum(tmp_f['count'])) * 100 for ii in range(len(tmp_f['count']))])
			nmax=min(nmax,len(excee_f))

			ensemble[i,:nmax]=(excee_f[0:nmax]-excee_h[0:nmax])/excee_h[0:nmax]*100

			n2 = state_count[dataset,season,state,region,'Plus20-Future']
			n1 = state_count[dataset,season,state,region,'All-Hist']

			cutoff_short = 2
			last_point = min(35,np.where(excee_h>0)[0][-1])
			y = excee_h[cutoff_short:last_point]
			x = np.arange(cutoff_short,last_point)
			y[np.isfinite(y) == False] = 0
			notna = np.where(np.isfinite(y))[0]
			y,x = y[notna],x[notna]
			popt, pcov = curve_fit(func, x, y)
			a,tau1 = popt

			days = np.arange(0,last_point,1)
			excee_y_h = func(days,*popt)
			excee_y_h = excee_y_h / excee_y_h[0] * 100
			#excee_y_h = np.array([np.sum(prob_y_h[ii:])/float(np.sum(prob_y_h)) * 100 for ii in range(len(prob_y_h))])

			p1 = np.exp(1./tau1)
			p2 = p1 * n2 / n1
			tau2_ = 1./np.log( (p2 ) )
			tau2 = tau1 / (1. + tau1*np.log(n2 / n1))
			if region == 'CEU':
				print(tau1,tau2,n2/n1,tau2/tau1)
			# tau2 = 1./np.log( (p1 / state_change ) )
			excee_y_f = func(days,a,tau2)
			excee_y_f = excee_y_f / excee_y_f[0] * 100

			#prob_y_f = prob_y_f / np.sum(prob_y_f)
			#excee_y_f = np.array([np.sum(prob_y_f[ii:])/float(np.sum(prob_y_f)) * 100 for ii in range(len(prob_y_f))])

			ensemble_fit[i,:min(35,last_point)]=(excee_y_f-excee_y_h)/excee_y_h*100




		subax.plot(range(1,nmax+1),np.nanmean(ensemble[:,0:nmax],axis=0),color=color,linestyle='-')
		subax.fill_between(range(1,nmax+1),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=color,alpha=0.3,edgecolor=color)

		subax.plot(range(2,nmax+1),np.nanmean(ensemble_fit[:,1:nmax],axis=0),color=arg1,linestyle='-')
		subax.fill_between(range(2,nmax+1),np.nanmin(ensemble_fit[:,1:nmax],axis=0),np.nanmax(ensemble_fit[:,1:nmax],axis=0),facecolor=arg1,alpha=0.3,edgecolor=arg1)



	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.05, 0.05), xycoords='axes fraction', color='black', weight='bold', fontsize=10)


plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

ensemble = None

def axis_settings(subax,label=False,arg1=None,arg2=None,arg3=None,arg4=None):
	subax.set_xlim((0,35))
	subax.set_ylim((-75,100))
	subax.plot([0,35],[0,0],'k')
	subax.set_xticks([7,14,21,28,35])
	subax.tick_params(axis='x',which='both',bottom=True,top=True,labelbottom=label,labelsize=8)
	subax.tick_params(axis='y',which='both',left=True,right=True,labelleft=label,labelsize=8)
	subax.locator_params(axis = 'y', nbins = 5)
	subax.locator_params(axis = 'x', nbins = 5)
	subax.yaxis.get_label().set_backgroundcolor('w')
	for tick in subax.yaxis.get_major_ticks():
		tick.label.set_backgroundcolor('w')
		tick.label.set_fontweight('bold')
	for tick in subax.xaxis.get_major_ticks():
		tick.label.set_fontweight('bold')
	subax.tick_params(axis='y', colors='k')
	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)
	return(subax)


fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[164,9], \
	arg1='blue',
	arg2=['pr'],
	arg3=['5mm'],
	arg4=['#009ACD'],
	title='exceedance probabilites of persistence in JJA')
plt.savefig('plots/paper/NH_changes_estimates.png',dpi=600)

def axis_settings(subax,label=False,arg1=None,arg2=None,arg3=None,arg4=None):
	subax.set_xlim((0,35))
	subax.set_ylim((-15,20))
	subax.plot([0,35],[0,0],'k')
	subax.set_xticks([7,14,21,28,35])
	subax.tick_params(axis='x',which='both',bottom=True,top=True,labelbottom=label,labelsize=8)
	subax.tick_params(axis='y',which='both',left=True,right=True,labelleft=label,labelsize=8)
	subax.locator_params(axis = 'y', nbins = 5)
	subax.locator_params(axis = 'x', nbins = 5)
	subax.yaxis.get_label().set_backgroundcolor('w')
	for tick in subax.yaxis.get_major_ticks():
		tick.label.set_backgroundcolor('w')
		tick.label.set_fontweight('bold')
	for tick in subax.xaxis.get_major_ticks():
		tick.label.set_fontweight('bold')
	subax.tick_params(axis='y', colors='k')
	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)
	return(subax)


fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[164,9], \
	arg1='red',
	arg2=['pr'],
	arg3=['dry'],
	arg4=['#FF8C00'],
	title='exceedance probabilites of persistence in JJA')
plt.savefig('plots/paper/NH_changes_estimates_dry.png',dpi=600)











#
