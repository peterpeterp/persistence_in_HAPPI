import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import matplotlib.pylab as plt
import matplotlib
import dimarray as da
from statsmodels.sandbox.stats import multicomp
import seaborn as sns
sns.set()
import cartopy.crs as ccrs
import cartopy

cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", sns.color_palette("cubehelix", 8)[::-1])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

data={}
for style in ['tas','pr','cpd']:
	data[style] = da.read_nc('data/EOBS/'+style+'_EOBS_SummaryMeanQu.nc')['SummaryMeanQu']

lat,lon = data[style].lat,data[style].lon

season='JJA'

color_range={'warm':{'mean':(3,7),'qu_95':(5,20)},
			'cold':{'mean':(3,7),'qu_95':(5,20)},
			'dry':{'mean':(3,14),'qu_95':(5,20)},
			'wet':{'mean':(1,4),'qu_95':(2,10)},
			'dry-warm':{'mean':(1,4),'qu_95':(5,14)},
			'wet-cold':{'mean':(1,4),'qu_95':(4,10)},
			}

# ------------------- cold-warm mean
plt.close('all')
fig,axes = plt.subplots(nrows=7,ncols=2,figsize=(4,5.5),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[1,4,4,4,4,4,4]})

for ax in axes[0,:]:
	ax.outline_patch.set_edgecolor('white')

for ax in axes[1:,:].flatten():
	ax.coastlines(edgecolor='black')
	ax.set_extent([-40,60,20,80],crs=ccrs.PlateCarree())

for style,state,row in zip(['tas','tas','pr','pr','cpd','cpd'],['warm','cold','dry','wet','dry-warm','wet-cold'],range(1,7)):

	for stat,ax,col in zip(['mean','qu_95'],axes[row,:],[0,2]):

		crange=color_range[state][stat]
		to_plot=data[style]['All-Hist',season,state,stat]
		im=ax.pcolormesh(lon,lat,to_plot ,vmin=crange[0],vmax=crange[1],cmap=cmap,transform=ccrs.PlateCarree());
		ax.annotate(state+'\n'+stat, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')
		cb=fig.colorbar(im,orientation='vertical',label='',ax=ax)
		tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
		cb.locator = tick_locator
		cb.update_ticks()

plt.annotate(s='mean persistence [days]', xy=(0.55,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=12,rotation='90')
plt.annotate(s='95th percentile of persistence [days]', xy=(0.97,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=12,rotation='90')

plt.suptitle('climatology EOBS', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/paper/FigureSI1_climatology_EOBS.png',dpi=300)


#sdasd
