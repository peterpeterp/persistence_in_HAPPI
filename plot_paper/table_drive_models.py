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

model_shifts = {
	'CAM4-2degree':(-0.25,-0.25),
	'ECHAM6-3-LR':(+0.25,-0.25),
	'MIROC5':(+0.25,+0.25),
	'NorESM1':(-0.25,+0.25),
}

x_wi = 0.25
y_wi = 0.25

def plot_column(ax,x,var, signi=None, c_range=(-0.1,0.1), label='label'):
	ax.axvline(x-0.5,color='k')
	ax.text(x,13.7,"\n".join(textwrap.wrap(label,15)),ha='center',va='bottom',rotation=90,fontsize=8)
	patches = []
	colors = []
	for y,region in zip(np.arange(0.5,len(regions)+0.5),regions):
		for model in var.model:
			x_shi,y_shi = model_shifts[model]
			polygon = Polygon([(x+x_shi-x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi+y_wi),(x+x_shi-x_wi,y+y_shi+y_wi)], True)
			patches.append(polygon)
			colors.append(var[model,region])
			if signi is not None:
				if signi[model,region] > 0.9:
					ax.plot(x+x_shi,y+y_shi,'*k')

	p = PatchCollection(patches, cmap=matplotlib.cm.RdBu_r, alpha=1)
	p.set_array(np.array(colors))
	p.set_clim(c_range)
	ax.add_collection(p)

	return ax

regions = {'EAS':1,
			'TIB':2,
			'CAS':3,
			'WAS':4,
			'MED':5,
			'CEU':6,
			'ENA':7,
			'CNA':8,
			'WNA':9,
			'NAS':10,
			'NEU':11,
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

summary = da.read_nc('data/driver_summary/*',align=True,axis='model')
summary.model = [mm.split('_')[-1] for mm in summary.model]

ax = plot_column(ax,2,var=summary['mean'][:,'warm','EKE','All-Hist',:,'corrcoef_all','JJA'], signi=summary['agree-signi'][:,'warm','EKE','All-Hist',:,'corrcoef_all','JJA'], label='warm - EKE corr')

var = summary['mean'][:,'warm','EKE','Plus20-Future',:,'mean_EKE','JJA'] - summary['mean'][:,'warm','EKE','All-Hist',:,'mean_EKE','JJA']
ax = plot_column(ax,3,var=var, c_range=(-0.001,0.001), label='cahnge EKE')


ax = plot_column(ax,12,var=summary['mean'][:,'warm','SPI3','All-Hist',:,'corrcoef_all','JJA'], signi=summary['agree-signi'][:,'warm','SPI3','All-Hist',:,'corrcoef_all','JJA'], label='warm - SPI3 corr')


ax = plot_column(ax,5,var=summary['mean'][:,'dry-warm','EKE','All-Hist',:,'corrcoef_all','JJA'], signi=summary['agree-signi'][:,'dry-warm','EKE','All-Hist',:,'corrcoef_all','JJA'], label='dry-warm - EKE corr')

ax = plot_column(ax,6,var=summary['mean'][:,'dry-warm','SPI3','All-Hist',:,'corrcoef_all','JJA'], signi=summary['agree-signi'][:,'dry-warm','SPI3','All-Hist',:,'corrcoef_all','JJA'], label='dry-warm - SPI3 corr')


ax = plot_column(ax,8,var=summary['mean'][:,'5mm','EKE','All-Hist',:,'corrcoef_all','JJA'], signi=summary['agree-signi'][:,'5mm','EKE','All-Hist',:,'corrcoef_all','JJA'], label='5mm - EKE corr')

ax = plot_column(ax,9,var=summary['mean'][:,'5mm','SPI3','All-Hist',:,'corrcoef_all','JJA'], signi=summary['agree-signi'][:,'5mm','SPI3','All-Hist',:,'corrcoef_all','JJA'], label='5mm - SPI3 corr')


ax.set_xlim(0,15)
ax.set_ylim(0,17)


fig.tight_layout()
plt.savefig('plots/table_models.pdf')
