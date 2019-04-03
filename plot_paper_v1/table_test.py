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

EKE = da.read_nc('data/EKE_summerMean_srex.nc')['EKE']
pers = da.read_nc('data/JJA_summary_srex.nc')['exceed_prob']

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()
srex['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}
for region in srex.keys():
	srex[region]['av_lat']=shapely.geometry.polygon.Polygon(srex[region]['points']).centroid.xy[1][0]

# colors=['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']

regions = ['ENA','CAS','NAS','CNA','NEU','WAS','TIB','CGI','MED','WNA','ALA','CEU','EAS']
colors=sns.color_palette("cubehelix", 15)[::-1]

regions = np.array(regions)[np.argsort([47.5 - np.abs(srex[region]['av_lat'] - 47.5 ) for region in regions])]

table = np.random.rand(6 ,5)

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
		ax.axhline(y-0.5,color='k')
		ax.text(0,y,region,va='center')
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

plt.close('all')
fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(8,6))
ax.axis('off')

for y_reg,region in zip(np.arange(0.5,len(regions)+0.5),regions):
	ax.axhline(y_reg-0.5,color='k')
	ax.text(0,y_reg,region,va='center')
ax.axhline(y_reg+0.5,color='k')

dummy = da.DimArray(np.random.rand(4 ,34),axes=EKE[:,'All-Hist',:].axes, dims=EKE[:,'All-Hist',:].dims)
for region in dummy.region:
	dummy[:,region] += np.random.random()*2
ax = plot_column(ax, x=2, var=dummy, c_range=[-3,3], label='corr. longest period in month vs EKE of month')

dummy = da.DimArray(np.random.rand(4 ,34),axes=EKE[:,'All-Hist',:].axes, dims=EKE[:,'All-Hist',:].dims)
for region in dummy.region:
	dummy[:,region] += np.random.random()*2
ax = plot_column(ax, x=3, var=dummy, c_range=[-3,3], label='change in monthly EKE')

dummy = da.DimArray(np.random.rand(4 ,34),axes=EKE[:,'All-Hist',:].axes, dims=EKE[:,'All-Hist',:].dims)
for region in dummy.region:
	dummy[:,region] -= np.random.random()*2
ax = plot_column(ax, x=4, var=dummy, c_range=[-3,3], label='change in longest period of month')

dummy = da.DimArray(np.random.rand(4 ,34),axes=EKE[:,'All-Hist',:].axes, dims=EKE[:,'All-Hist',:].dims)
for region in dummy.region:
	dummy[:,region] += np.random.random()*2
ax = plot_column(ax, x=5, var=dummy, c_range=[-3,3], label='corr. longest period in month vs SPI3 of month')

dummy = da.DimArray(np.random.rand(4 ,34),axes=EKE[:,'All-Hist',:].axes, dims=EKE[:,'All-Hist',:].dims)
for region in dummy.region:
	dummy[:,region] += np.random.random()*2
ax = plot_column(ax, x=6, var=dummy, c_range=[-3,3], label='change in monthly SPI3')

patches = []
for model in EKE.model:
	x_shi,y_shi = model_shifts[model]
	polygon = Polygon([(10+x_shi-x_wi,15+y_shi-y_wi),(10+x_shi+x_wi,15+y_shi-y_wi),(10+x_shi+x_wi,15+y_shi+y_wi),(10+x_shi-x_wi,15+y_shi+y_wi)], True)
	ax.annotate(model, xy=(10+ x_shi,15+ y_shi), xytext=(10+x_shi*4,15+y_shi*4),arrowprops=dict(facecolor='k',edgecolor='k', arrowstyle="->"),fontsize=10,color='k',ha='center')

	patches.append(polygon)
p = PatchCollection(patches, cmap=matplotlib.cm.RdBu, alpha=1)
p.set_array(np.array(range(4)))
ax.add_collection(p)

ax.set_xlim(0,13)
ax.set_ylim(0,16)


fig.tight_layout()
plt.savefig('plots/table_test.pdf')
