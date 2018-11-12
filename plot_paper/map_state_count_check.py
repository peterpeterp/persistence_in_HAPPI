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

color_range={'warm':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'cold':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'dry':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'wet':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'dry-warm':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'wet-cold':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'wet-cold':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			}

# ------------------- cold-warm mean
plt.close('all')
asp=0.5
fig,axes = plt.subplots(nrows=4,ncols=2,figsize=(8,4),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[4,4,4,4]})

for ax in axes[:,:].flatten():
	ax.coastlines(edgecolor='black')
	ax.set_extent([-180,180,0,80],crs=ccrs.PlateCarree())

for model,row in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
	ax= axes[row,0]

	state_days = da.read_nc('data/'+model+'/state_stats/'+model+'_stateCount_1x1.nc')['*'.join(['All-Hist','JJA','dry'])]
	state_days = np.abs(state_days / (91*1000)) *100

	lat,lon = state_days.lat,state_days.lon
	lon=np.roll(lon,len(lon)/2)

	to_plot=np.roll(state_days,len(lon)/2,axis=-1)
	im=ax.pcolormesh(lon,lat,to_plot ,cmap=cmap,transform=ccrs.PlateCarree());
	ax.annotate(model, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')
	cb=fig.colorbar(im,orientation='vertical',label='',ax=ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

for model,row in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
	ax= axes[row,1]

	hist_days = da.read_nc('data/'+model+'/state_stats/'+model+'_stateCount_1x1.nc')['*'.join(['All-Hist','JJA','dry'])]
	hist_days = np.abs(hist_days / (91*10*100)) *100
	fut_days = da.read_nc('data/'+model+'/state_stats/'+model+'_stateCount_1x1.nc')['*'.join(['Plus20-Future','JJA','dry'])]
	fut_days = np.abs(fut_days / (91*10*100)) *100

	lat,lon = state_days.lat,state_days.lon
	lon=np.roll(lon,len(lon)/2)

	to_plot=np.roll(fut_days-hist_days,len(lon)/2,axis=-1)
	im=ax.pcolormesh(lon,lat,to_plot ,cmap=cmap_change,transform=ccrs.PlateCarree(), vmin=-10,vmax=10);
	ax.annotate(model, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')
	cb=fig.colorbar(im,orientation='vertical',label='',ax=ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

plt.annotate(s='state fraction in 2006-2015 [%]', xy=(0.5,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=12,rotation='90')
plt.annotate(s='differene in state fraction +2$^\circ$C vs 2006-2015 [%]', xy=(0.97,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=12,rotation='90')

fig.tight_layout()
plt.savefig('plots/paper/map_state_percentage_check.png',dpi=300)


#sdasd
