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

color_range={'warm':(0,100),
			'dry':(0,100),
			'dry-warm':(0,50),
			'5mm':(0,50),
			'10mm':(0,50),
			}

for state,row,letter in zip(['dry','dry-warm','5mm'],range(3),['a','b','c']):
	ax= axes[row]
	ax.annotate(letter, xy=(0.00, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=12, horizontalalignment='left', backgroundcolor='w')

	ensemble=np.zeros([4,180,360])*np.nan
	for model,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
		state_days = da.read_nc('data/'+model+'/state_stats/'+model+'_stateCount_1x1.nc')['*'.join(['All-Hist','JJA',state])]
		ensemble[i,:,:] = state_days *100

	lat,lon = state_days.lat,state_days.lon
	lon=np.roll(lon,len(lon)/2)

	to_plot=np.roll(np.nanmean(ensemble,axis=0),len(lon)/2,axis=-1)
	to_plot[to_plot == 0] = np.nan
	im=ax.pcolormesh(lon,lat,to_plot ,cmap=cmap,transform=ccrs.PlateCarree(), vmin=color_range[state][0], vmax=color_range[state][1]);
	ax.annotate(legend_dict[state], xy=(0.02, 0.05), xycoords='axes fraction',fontweight='bold',fontsize=8)
	cb=fig.colorbar(im,orientation='vertical',label='',ax=ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

plt.annotate(s='state fraction in 2006-2015 [%]', xy=(0.97,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=8,rotation='90')
fig.tight_layout()
plt.savefig('plots/paper/map_state_percentage.png',dpi=300)

plt.close('all')
fig,axes = plt.subplots(nrows=3,ncols=1,figsize=(4,3),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[4,4,4]})

for ax in axes[:].flatten():
	ax.coastlines(edgecolor='black')
	ax.set_extent([-180,180,0,80],crs=ccrs.PlateCarree())

color_range={'warm':(0,100),
			'dry':(0,100),
			'dry-warm':(0,50),
			'5mm':(0,50),
			'10mm':(0,50),
			}

for state,row,letter in zip(['dry','dry-warm','5mm'],range(3),['a','b','c']):
	ax= axes[row]
	ax.annotate(letter, xy=(0.00, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=12, horizontalalignment='left', backgroundcolor='w')

	ensemble=np.zeros([4,180,360])*np.nan
	for model,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
		hist_days = da.read_nc('data/'+model+'/state_stats/'+model+'_stateCount_1x1.nc')['*'.join(['All-Hist','JJA',state])]
		fut_days = da.read_nc('data/'+model+'/state_stats/'+model+'_stateCount_1x1.nc')['*'.join(['Plus20-Future','JJA',state])]
		ensemble[i,:,:] = (fut_days - hist_days) / hist_days * 100


	#aggree = np.roll(np.sum(np.sign(ensemble),axis=0),len(lon)/2,axis=-1)
	aggree = np.sum(np.sign(ensemble),axis=0)

	lat,lon = state_days.lat,state_days.lon
	#lon=np.roll(lon,len(lon)/2)

	to_plot=np.nanmean(ensemble,axis=0)
	#to_plot=np.roll(np.nanmean(ensemble,axis=0),len(lon)/2,axis=-1)
	im=ax.pcolormesh(lon,lat,to_plot ,cmap=cmap_change,transform=ccrs.PlateCarree(), vmin=-15,vmax=15);
	im__=ax.contourf(lon,lat,aggree , hatches=['/'*7],levels=[-2,2],colors=['none'], transform=ccrs.PlateCarree());
	ax.annotate(legend_dict[state], xy=(0.02, 0.05), xycoords='axes fraction', fontsize=8,fontweight='bold')
	cb=fig.colorbar(im,orientation='vertical',label='',ax=ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

plt.annotate(s='differene in state fraction \n+2$^\circ$C vs 2006-2015 [%]', xy=(0.97,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=8,rotation='90')

fig.tight_layout()
plt.savefig('plots/paper/map_state_stats_change.png',dpi=300)


#sdasd
