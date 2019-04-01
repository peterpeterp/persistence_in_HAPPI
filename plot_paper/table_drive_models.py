import os,sys,glob,time,collections,gc,pickle,textwrap
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
from statsmodels.sandbox.stats import multicomp
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection

import matplotlib
import cartopy.crs as ccrs
import cartopy
import seaborn as sns
import shapely
sns.set()
sns.set_style("whitegrid")
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

def plot_model_column(ax,x,var,signi=None,label=' ',c_range=(-0.5,0.5)):
	patches = []
	colors = []
	ax.axvline(x-0.5,color='k')
	ax.text(x,13.7,"\n".join(textwrap.wrap(label,15)),ha='center',va='bottom',rotation=90,fontsize=8)
	for region,y in regions.items():
		for model in model_shifts.keys():
			x_shi,y_shi = model_shifts[model]
			polygon = Polygon([(x+x_shi-x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi+y_wi),(x+x_shi-x_wi,y+y_shi+y_wi)], True)

			if np.isfinite(var[model,region]):
				patches.append(polygon)
				colors.append(var[model,region])

	p = PatchCollection(patches, cmap=matplotlib.cm.RdBu_r, alpha=1)
	p.set_array(np.array(colors))
	p.set_clim(c_range)
	ax.add_collection(p)

model_shifts = {
	'CAM4-2degree':(-0.25,-0.25),
	'ECHAM6-3-LR':(+0.25,-0.25),
	'MIROC5':(+0.25,+0.25),
	'NorESM1':(-0.25,+0.25),
}

x_wi = 0.25
y_wi = 0.25

regions = {'EAS':1,
			'TIB':2,
			'CAS':3,
			'WAS':4,
			'MED':5,
			'CEU':6,
			'NEU':7,
			'NAS':8,
			'ENA':9,
			'CNA':10,
			'WNA':11,
			'CGI':12,
			'ALA':13,
}

plt.close('all')
fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(8,6))
ax.axis('off')

for region,y_reg in regions.items():
	ax.axhline(y_reg-0.5,color='k')
	ax.text(0,y_reg,region,va='center')
ax.axhline(13+0.5,color='k')

summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']

x=1
for state in ['warm']:	#,'dry','dry-warm','5mm'
	for corWith in ['EKE','SPI3']:
		x += 1
		plot_model_column(ax,x,summary['All-Hist',:,state,corWith,:,'corrcoef_all','JJA'], label=corWith+' '+state+' cor')

		x += 1
		var = summary['Plus20-Future',:,state,corWith,:,'mean_'+corWith,'JJA'] - summary['All-Hist',:,state,corWith,:,'mean_'+corWith,'JJA']
		plot_model_column(ax,x,var,label = 'change '+corWith)

		x += 1
		diff_cor = summary['Plus20-Future',:,state,corWith,:,'mean_'+corWith,'JJA']  - summary['All-Hist',:,state,corWith,:,'mean_'+corWith,'JJA']
		var = diff_cor / summary['All-Hist',:,state,corWith,:,'lr_slope','JJA']
		asdad
		plot_model_column(ax,x,var, label='change '+state+' due to '+corWith)

		x += 1
		var = summary['Plus20-Future',:,state,corWith,:,'mean_'+state,'JJA'] - summary['All-Hist',:,state,corWith,:,'mean_'+state,'JJA']
		plot_model_column(ax,x,var,label = 'change '+state)


ax.set_xlim(0,15)
ax.set_ylim(0,17)


fig.tight_layout()
plt.savefig('plots/table_models.pdf')
