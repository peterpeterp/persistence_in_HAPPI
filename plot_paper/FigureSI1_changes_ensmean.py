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

cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

if 'sum_meanQu' not in globals():
	sum_meanQu={}
	for style in ['tas','pr','cpd']:
		sum_meanQu[style]={}
		for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
			sum_meanQu[style][model]=da.read_nc('data/'+model+'/'+style+'_'+model+'_SummaryMeanQu_1x1.nc')

lat,lon = sum_meanQu[style][model].lat,sum_meanQu[style][model].lon
lon=np.roll(lon,180)

season='JJA'

color_range={'warm':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'cold':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'dry':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'wet':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'dry-warm':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			'wet-cold':{'mean':(-0.25,0.25),'qu_95':(-0.5,0.5)},
			}

# ------------------- cold-warm mean
plt.close('all')
asp=0.5
fig,axes = plt.subplots(nrows=7,ncols=2,figsize=(8,6),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[1,4,4,4,4,4,4]})

for ax in axes[0,:]:
	ax.outline_patch.set_edgecolor('white')

for ax in axes[1:,:].flatten():
	ax.coastlines(edgecolor='black')
	ax.set_extent([-180,180,0,80],crs=ccrs.PlateCarree())

for style,state,row in zip(['tas','tas','pr','pr','cpd','cpd'],['warm','cold','dry','wet','dry-warm','wet-cold'],range(1,7)):

	for stat,ax,col in zip(['mean','qu_95'],axes[row,:],[0,2]):
		ensemble=np.zeros([4,lat.shape[0],lon.shape[0]])*np.nan
		for model,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
			ensemble[i,:,:]=sum_meanQu[style][model]['*'.join(['Plus20-Future',season,state,stat])] - sum_meanQu[style][model]['*'.join(['All-Hist',season,state,stat])]

		crange=color_range[state][stat]
		to_plot=np.roll(np.nanmean(ensemble,axis=0),180,axis=-1)
		im=ax.pcolormesh(lon,lat,to_plot ,vmin=crange[0],vmax=crange[1],cmap=cmap,transform=ccrs.PlateCarree());
		ax.annotate(state+'\n'+stat, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')
		cb=fig.colorbar(im,orientation='vertical',label='',ax=ax)
		tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
		cb.locator = tick_locator
		cb.update_ticks()

plt.annotate(s='changes in mean persistence [days]', xy=(0.5,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=12,rotation='90')
plt.annotate(s='changes in 95th percentile of persistence [days]', xy=(0.97,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=12,rotation='90')

plt.suptitle('ensemble mean difference +2$^\circ$C vs 2006-2015', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/paper/FigureSI1_changes_ensmean.png',dpi=300)


#sdasd
