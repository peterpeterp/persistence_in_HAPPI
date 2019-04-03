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

if 'exceedanceProb' not in globals():
	exceedanceProb={}
	for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
		exceedanceProb[model]=da.read_nc('data/'+model+'/'+model+'_EsceedanceProb_gridded_1x1.nc')

lat,lon = exceedanceProb[model].lat,exceedanceProb[model].lon
lon=np.roll(lon,180)

season='JJA'

color_range={'warm':{14:(-15,15),21:(-15,15)},
			'dry':{14:(-30,30),21:(-30,30)},
			'dry-warm':{14:(-30,30),21:(-30,30)},
			'5mm':{7:(-30,30),7:(-30,30)},
			'10mm':{3:(-30,30),5:(-30,30)},
			}

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rainy'}

# ------------------- cold-warm mean
plt.close('all')
fig,axes = plt.subplots(nrows=4,ncols=1,figsize=(4,4),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[4,4,4,4]})

# axes[0].outline_patch.set_edgecolor('white')

for ax in axes[:].flatten():
	ax.coastlines(edgecolor='black')
	ax.set_extent([-180,180,0,80],crs=ccrs.PlateCarree())

for state,row,letter in zip(['warm','dry','dry-warm','5mm'],range(5),['a','b','c','d']):

	#for stat,ax,col in zip(sorted(color_range[state].keys()),axes[row,:],[0,2]):
	stat = sorted(color_range[state].keys())[0]
	ax=axes[row]
	ax.annotate(letter, xy=(0.00, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=12, horizontalalignment='left', backgroundcolor='w')

	ensemble=np.zeros([4,lat.shape[0],lon.shape[0]])*np.nan
	for model,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
		ensemble[i,:,:]=(exceedanceProb[model]['*'.join(['Plus20-Future',season,state,str(stat)])] - exceedanceProb[model]['*'.join(['All-Hist',season,state,str(stat)])]) / exceedanceProb[model]['*'.join(['All-Hist',season,state,str(stat)])] * 100

	crange=color_range[state][stat]
	to_plot=np.roll(np.nanmean(ensemble,axis=0),180,axis=-1)
	im=ax.pcolormesh(lon,lat,to_plot ,vmin=crange[0],vmax=crange[1],cmap=cmap,transform=ccrs.PlateCarree());

	aggree = np.sum(np.sign(ensemble),axis=0)
	im__=ax.contourf(np.roll(lon,180,axis=-1),lat,aggree , hatches=['/'*5],levels=[-2,2],colors=['none'], transform=ccrs.PlateCarree());

	ax.annotate(legend_dict[state]+'\n'+str(stat)+'-day', xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')
	cb=fig.colorbar(im,orientation='vertical',label='',ax=ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

plt.annotate(s='relative change exceedance probabilities [%]', xy=(0.97,0.5), xycoords='figure fraction',va='center', ha='center',fontsize=12,rotation='90')

#plt.suptitle('ensemble mean difference +2$^\circ$C vs 2006-2015', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/paper/map_exceedanceProb_changes_ensmean.png',dpi=300)


#sdasd
