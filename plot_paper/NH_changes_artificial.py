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
	for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
		infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
		pkl_file=open(infile, 'rb')
		big_dict[dataset] = pickle.load(pkl_file);	pkl_file.close()


		infile = 'data/artificial/'+model+'_regional_distrs_srex_artificial.pkl'
		pkl_file=open(infile, 'rb')
		tmp = pickle.load(pkl_file);	pkl_file.close()
		for region in tmp.keys():
			big_dict[dataset][region]['Plus20-Artificial-v1'] = tmp[region]['Plus20-Artificial-v1']


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
		'mid-lat':{'edge':'darkgreen','color':'none','alpha':1,'pos':(-148,35),'xlabel':'Period length [days]','ylabel':'Exceedence probability [%]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1.3}}

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

def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	season=all_regs[region][arg1]
	for style,state,color,hatch in zip(arg2[::-1],arg3[::-1],arg4[::-1],arg5[::-1]):
		ensemble=np.zeros([4,35])*np.nan
		nmax=35
		for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
			tmp_20=big_dict[dataset][region]['Plus20-Artificial-v1'][state][season]
			tmp_h=big_dict[dataset][region]['All-Hist'][state][season]
			count_20=np.array([np.sum(tmp_20['count'][ii:])/float(np.sum(tmp_20['count'])) for ii in range(len(tmp_20['count']))])
			count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) for ii in range(len(tmp_h['count']))])
			nmax=min(len(count_20),len(count_h),nmax)
			tmp=(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100
			ensemble[i,:nmax]=tmp

		subax.plot(range(1,nmax+1),np.nanmean(ensemble[:,0:nmax],axis=0),color=color,linestyle='-')
		subax.fill_between(range(1,nmax+1),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=color, edgecolor=color,alpha=0.3)

	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.05, 0.05), xycoords='axes fraction', color='black', weight='bold', fontsize=10)

def axis_settings(subax,label=False,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.set_xlim((0,35))
	subax.set_ylim(c_range)
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

plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rain'}

plt.close('all')
with PdfPages('plots/NH_changes_artificial.pdf') as pdf:
	arg2 = ['pr','pr']
	arg3 = ['dry','5mm']
	arg4 = ['#FF8C00','#009ACD']
	arg5 = ['/'*3,'\ '*3,'|'*3,'-'*3]
	c_range = [(-15,20),(-15,20),(-15,20),(-50,100)]
	for combi in [[0],[1]]:
		arg2_,arg3_,arg4_,arg5_ = [],[],[],[]
		for aa,aa_all in zip([arg2_,arg3_,arg4_,arg5_],[arg2,arg3,arg4,arg5]):
			for co in combi:
				aa.append(aa_all[co])
		if combi != [3]:
			c_range = (-200,200)
		else:
			c_range = (-200,200)
		fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[164,9], \
			arg1='summer',
			arg2=arg2_,
			arg3=arg3_,
			arg4=arg4_,
			arg5=arg5_,
			title=None)

		plt.tight_layout(); pdf.savefig(); plt.close()



region = 'CGI'
tmp_arti=big_dict['MIROC5'][region]['Plus20-Artificial-v1']['dry']['JJA']
tmp_20=big_dict['MIROC5'][region]['Plus20-Future']['dry']['JJA']
tmp_h=big_dict['MIROC5'][region]['All-Hist']['dry']['JJA']
maxlen = min([len(tmp_20['count']),len(tmp_h['count']),len(tmp_arti['count'])])
print(tmp_20['count'][:80] - tmp_h['count'][:80])
print(tmp_arti['count'][:80] - tmp_h['count'][:80])
print(tmp_arti['count'][:maxlen] - tmp_20['count'][:maxlen])

print(sum(tmp_h['count']))
print(sum(tmp_arti['count']))
print(sum(tmp_20['count']))






#
