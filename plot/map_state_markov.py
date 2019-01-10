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
cmap_change = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

season='JJA'

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rainy'}

# ------------------- cold-warm mean
plt.close('all')
asp=0.5
fig,axes = plt.subplots(nrows=3,ncols=1,figsize=(4,3),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[4,4,4]})

for ax in axes[:].flatten():
	ax.coastlines(edgecolor='black')
	ax.set_extent([-180,180,0,80],crs=ccrs.PlateCarree())

color_range={'dry':{'cb':(0,100),'len':14},
			'dry-warm':{'cb':(0,1),'len':14},
			'5mm':{'cb':(0,0.5),'len':7},
			}

for state,row in zip(['dry-warm','dry','5mm'],range(3)):
	ax= axes[row]

	ensemble=np.zeros([4,180,360])*np.nan
	for model,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
		state_days = da.read_nc('data/'+model+'/state_stats/'+model+'_stateCount_1x1.nc')['*'.join(['All-Hist','JJA',state])]
		ensemble[i,:,:] = state_days

	lat,lon = state_days.lat,state_days.lon
	lon=np.roll(lon,len(lon)/2)

	state_perc=np.roll(np.nanmean(ensemble,axis=0),len(lon)/2,axis=-1)

	exceed_prob = state_perc*0
	for i in range(14,40):
		exceed_prob += state_perc ** i

	asdas

	to_plot[to_plot == 0] = np.nan
	im=ax.pcolormesh(lon,lat,to_plot ,cmap=cmap,transform=ccrs.PlateCarree(), vmin=color_range[state]['cb'][0], vmax=color_range[state]['cb'][1]);
	ax.annotate(legend_dict[state], xy=(0.02, 0.05), xycoords='axes fraction',fontweight='bold',fontsize=8)
	cb=fig.colorbar(im,orientation='vertical',label='',ax=ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

plt.annotate(s='state fraction in 2006-2015 [%]', xy=(0.97,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=8,rotation='90')
fig.tight_layout()
plt.savefig('plots/paper/map_state_markov.png',dpi=300)
