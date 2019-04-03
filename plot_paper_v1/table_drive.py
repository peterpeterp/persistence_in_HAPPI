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

def plot_column(ax,x,var,c_range=None, label='label'):
	ax.axvline(x-0.5,color='k')
	ax.text(x,13.2,"\n".join(textwrap.wrap(label,15)),ha='center',va='bottom',rotation=90,fontsize=8)
	patches = []
	colors = []
	for y,region in zip(np.arange(0.5,len(regions)+0.5),regions):
		for model in EKE.model:
			x_shi,y_shi = model_shifts[model]
			polygon = Polygon([(x+x_shi-x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi+y_wi),(x+x_shi-x_wi,y+y_shi+y_wi)], True)
			patches.append(polygon)
			colors.append(var[model,region])

	p = PatchCollection(patches, cmap=matplotlib.cm.RdBu, alpha=1)
	p.set_array(np.array(colors))
	p.set_clim(c_range)
	ax.add_collection(p)

	return ax


def plot_obs_column(ax,x,var,masks,c_range=None, label='label', x_shi=0 ,y_shi=0):
	ax.axvline(x-0.5,color='k')
	ax.text(x,13.7,"\n".join(textwrap.wrap(label,15)),ha='center',va='bottom',rotation=90,fontsize=8)
	patches = []
	colors = []
	for region,y in regions.items():
		mask = masks[region].copy()
		if mask.shape != var['corrcoef']['JJA'].shape:
			mask = mask.T
		cor = np.array(var['corrcoef']['JJA'].values * mask.values).flatten()
		relevant_cells = np.where((mask.flatten()>0) & (np.isfinite(cor)))[0]
		cor = cor[relevant_cells]

		patches.append(plt.Circle((x, y), 0.25))
		colors.append(np.nansum(cor))

		homogenety = np.sum( np.sign(cor) == np.sign(np.nansum(cor)) ) / float(cor.shape[0])
		if homogenety >= 0.9:
			ax.plot([x],[y],'*k')

		mask[mask>0] = 1
		pval = np.array(var['p_value']['JJA'].values * mask.values).flatten()
		signi = np.sum( (np.sign(cor) == np.sign(np.nansum(cor))) & (pval[relevant_cells] < 0.05) ) / float(cor.shape[0])
		if signi >= 0.5:
			ax.plot([x],[y],'vk')


	p = PatchCollection(patches, cmap=matplotlib.cm.RdBu_r, edgecolor='k', alpha=1)
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

had_mask = da.read_nc('masks/srex_mask_73x97.nc')
ax = plot_obs_column(ax, x=2, var=da.read_nc('data/HadGHCND/All-Hist/cor_EKE_HadGHCND_All-Hist_warm.nc'), label='corr. EKE warm pers',
						masks=had_mask, c_range=[-0.2,0.2])
ax = plot_obs_column(ax, x=3, var=da.read_nc('data/HadGHCND/All-Hist/corLongest_EKE_HadGHCND_All-Hist_warm.nc'), label='corr. EKE long warm pers',
						masks=had_mask, c_range=[-0.2,0.2])
ax = plot_obs_column(ax, x=4, var=da.read_nc('data/HadGHCND/All-Hist/cor_SPI3_HadGHCND_All-Hist_warm.nc'), label='corr. SPI3 warm pers',
						masks=had_mask, c_range=[-0.2,0.2])
ax = plot_obs_column(ax, x=5, var=da.read_nc('data/HadGHCND/All-Hist/corLongest_SPI3_HadGHCND_All-Hist_warm.nc'), label='corr. SPI3 long warm pers',
						masks=had_mask, c_range=[-0.2,0.2])

regions = {key:val for key,val in regions.items() if key in ['NEU','MED','CEU']}
eobs_mask = da.read_nc('masks/srex_mask_EOBS.nc')
ax = plot_obs_column(ax, x=6, var=da.read_nc('data/EOBS/All-Hist/cor_EKE_EOBS_All-Hist_dry.nc'), label='corr. EKE dry pers',
						masks=eobs_mask, c_range=[-0.2,0.2])
ax = plot_obs_column(ax, x=7, var=da.read_nc('data/EOBS/All-Hist/corLongest_EKE_EOBS_All-Hist_dry.nc'), label='corr. EKE long dry pers',
						masks=eobs_mask, c_range=[-0.2,0.2])
ax = plot_obs_column(ax, x=8, var=da.read_nc('data/EOBS/All-Hist/cor_SPI3_EOBS_All-Hist_dry.nc'), label='corr. SPI3 dry pers',
						masks=eobs_mask, c_range=[-0.2,0.2])
ax = plot_obs_column(ax, x=9, var=da.read_nc('data/EOBS/All-Hist/corLongest_SPI3_EOBS_All-Hist_dry.nc'), label='corr. SPI3 long dry pers',
						masks=eobs_mask, c_range=[-0.2,0.2])

ax = plot_obs_column(ax, x=10, var=da.read_nc('data/EOBS/All-Hist/cor_EKE_EOBS_All-Hist_5mm.nc'), label='corr. EKE 5mm pers',
						masks=eobs_mask, c_range=[-0.2,0.2])
ax = plot_obs_column(ax, x=11, var=da.read_nc('data/EOBS/All-Hist/corLongest_EKE_EOBS_All-Hist_5mm.nc'), label='corr. EKE long 5mm pers',
						masks=eobs_mask, c_range=[-0.2,0.2])
ax = plot_obs_column(ax, x=12, var=da.read_nc('data/EOBS/All-Hist/cor_SPI3_EOBS_All-Hist_5mm.nc'), label='corr. SPI3 5mm pers',
						masks=eobs_mask, c_range=[-0.2,0.2])
ax = plot_obs_column(ax, x=13, var=da.read_nc('data/EOBS/All-Hist/corLongest_SPI3_EOBS_All-Hist_5mm.nc'), label='corr. SPI3 long 5mm pers',
						masks=eobs_mask, c_range=[-0.2,0.2])
# ax = plot_obs_column(ax, x=8, var=da.read_nc('data/EOBS/All-Hist/cor_SPI3_EOBS_All-Hist_dry.nc'), label='corr. SPI3 dry pers',
# 						masks=eobs_mask, c_range=[-0.2,0.2])
# ax = plot_obs_column(ax, x=9, var=da.read_nc('data/EOBS/All-Hist/corLongest_SPI3_EOBS_All-Hist_dry.nc'), label='corr. SPI3 long dry pers',
# 						masks=eobs_mask, c_range=[-0.2,0.2])

# patches = []
# for model in EKE.model:
# 	x_shi,y_shi = model_shifts[model]
# 	polygon = Polygon([(10+x_shi-x_wi,15+y_shi-y_wi),(10+x_shi+x_wi,15+y_shi-y_wi),(10+x_shi+x_wi,15+y_shi+y_wi),(10+x_shi-x_wi,15+y_shi+y_wi)], True)
# 	ax.annotate(model, xy=(10+ x_shi,15+ y_shi), xytext=(10+x_shi*4,15+y_shi*4),arrowprops=dict(facecolor='k',edgecolor='k', arrowstyle="->"),fontsize=10,color='k',ha='center')
#
# 	patches.append(polygon)
# p = PatchCollection(patches, cmap=matplotlib.cm.RdBu, alpha=1)
# p.set_array(np.array(range(4)))
# ax.add_collection(p)

ax.set_xlim(0,15)
ax.set_ylim(0,17)


fig.tight_layout()
plt.savefig('plots/table_test.pdf')
