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


NH_regs={'ALA':{'color':'darkgreen','pos_off':(+0,+3),'summer':'JJA','winter':'DJF'},
		'WNA':{'color':'darkblue','pos_off':(+20,+15),'summer':'JJA','winter':'DJF'},
		'CNA':{'color':'gray','pos_off':(+8,-8),'summer':'JJA','winter':'DJF'},
		'ENA':{'color':'darkgreen','pos_off':(+23,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},
		# 'CAM':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'color':'darkgreen','pos_off':(-23,+5),'summer':'JJA','winter':'DJF'},
		'CEU':{'color':'darkblue','pos_off':(+6,+7),'summer':'JJA','winter':'DJF'},
		'CAS':{'color':'darkgreen','pos_off':(-3,+13),'summer':'JJA','winter':'DJF'},
		'NAS':{'color':'gray','pos_off':(-6,+11),'summer':'JJA','winter':'DJF'},
		'TIB':{'color':'darkcyan','pos_off':(-5,-16),'summer':'JJA','winter':'DJF'},
		'EAS':{'color':'darkgreen','pos_off':(-3,0),'summer':'JJA','winter':'DJF'},

		'MED':{'color':'gray','pos_off':(-16,-10),'summer':'JJA','winter':'DJF'},
		'WAS':{'color':'darkcyan','pos_off':(-7,-10),'summer':'JJA','winter':'DJF'},
		'mid-lat':{'edge':'darkgreen','color':'none','alpha':1,'pos':(-140,35),'summer':'JJA','winter':'DJF','scaling_factor':1.3}}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

#colors=['black']+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.axis('off')

def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.04, 0.07), xycoords='axes fraction', color='black', weight='bold', fontsize=8,backgroundcolor='w')

plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rain'}

plt.close('all')
size=13
reg_info=all_regs
x_ext=[-180,180]
y_ext=[0,85]
small_plot_size=0.08
asp=float(x_ext[-1]-x_ext[0])/float(y_ext[-1]-y_ext[0])
fig=plt.figure(figsize=(size,size/asp))
ax_map=fig.add_axes([0,0,1,1],projection=ccrs.Robinson(central_longitude=0, globe=None))
ax_map.set_global()
ax_map.coastlines()
ax_map.set_extent(x_ext+y_ext, crs=ccrs.PlateCarree())
ax_map.axis('off')

patches,colors=[],[]
for region in reg_info.keys():
	if region in polygons.keys():
		ax_map.add_geometries([Polygon(polygons[region]['points'])], ccrs.PlateCarree(), color=None,alpha=0.3,facecolor=reg_info[region]['color'],hatch=' ')
		if region=='mid-lat':
			ax_map.add_geometries([Polygon(polygons[region]['points'])], ccrs.PlateCarree(), color=reg_info[region]['edge'],alpha=1,facecolor=reg_info[region]['color'],linewidth=3)
			# ax_map.text(-160,50,region, color='black', weight='bold', fontsize=8,backgroundcolor='w', transform=ccrs.PlateCarree(), ha='center')
		else:
			x,y=Polygon(polygons[region]['points']).centroid.xy
			ax_map.text(x[0],y[0],region, color='black', weight='bold', fontsize=8,backgroundcolor='w', transform=ccrs.PlateCarree(), ha='center')


plt.tight_layout(); plt.savefig('plots/NH_regions.png',dpi=600); plt.close()












#
