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
from matplotlib.patches import Patch


cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

if 'exceedanceProb' not in globals():
	exceedanceProb={}
	for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree','HadGHCND']:
		exceedanceProb[model]=da.read_nc('data/'+model+'/'+model+'_EsceedanceProb_gridded_1x1.nc')

lat,lon = exceedanceProb[model].lat,exceedanceProb[model].lon
lon=np.roll(lon,180)

season='JJA'

color_range={'warm':{7:(-15,15),21:(-15,15)},
			'dry':{7:(-30,30),21:(-30,30)},
			'dry-warm':{7:(-30,30),21:(-30,30)},
			'5mm':{3:(-30,30),7:(-30,30)},
			'10mm':{3:(-30,30),5:(-30,30)},
			}

# ------------------- cold-warm mean
plt.close('all')
fig,axes = plt.subplots(nrows=6,ncols=5,figsize=(11,8),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[1,4,4,4,4,2],'width_ratios':[4,1,1,1,1]})

for ax in axes[1:-1,0].flatten():
	ax.coastlines(edgecolor='black')
	ax.set_extent([-180,180,0,80],crs=ccrs.PlateCarree())

for ax in axes[1:-1,1:].flatten():
	ax.coastlines(edgecolor='black')
	ax.set_extent([-15,60,10,80],crs=ccrs.PlateCarree())

for ax,letter in zip(axes[1:-1,:].T.flatten(),list(map(chr, range(97, 123)))):
	ax.annotate(letter, xy=(0.00, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=12, horizontalalignment='left', backgroundcolor='w')

for model,ax,letter in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],axes[1:-1,0],['a','b','c','d']):
	excee_bias =  (exceedanceProb[model]['*'.join(['All-Hist',season,'warm','7'])] - exceedanceProb['HadGHCND']['*'.join(['All-Hist',season,'warm','7'])]) / exceedanceProb['HadGHCND']['*'.join(['All-Hist',season,'warm','7'])] * 100

	im=ax.pcolormesh(np.roll(lon,180,axis=-1),lat,excee_bias, transform=ccrs.PlateCarree(), cmap='RdBu_r', vmin=-100,vmax=100);
	ax.annotate(model, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')

for col,state,excee in zip([1,2,3,4],['warm','dry','dry-warm','5mm'],['7','7','7','3']):
	for model,ax,letter in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],axes[1:-1,col],['a','b','c','d']):

		excee_bias =  (exceedanceProb[model]['*'.join(['All-Hist',season,state,excee])] - exceedanceProb['EOBS']['*'.join(['All-Hist',season,state,excee])]) / exceedanceProb['EOBS']['*'.join(['All-Hist',season,state,excee])] * 100

		im=ax.pcolormesh(np.roll(lon,180,axis=-1),lat,excee_bias, transform=ccrs.PlateCarree(), cmap='RdBu_r', vmin=-100,vmax=100);
		ax.annotate(model, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')

for col,state,excee,ref in zip([0,1,2,3,4],['warm','warm','dry','dry-warm','rain'],['7','7','7','7','3'],['HadGHCND','EOBS','EOBS','EOBS','EOBS']):
	axes[0,col].annotate(excee+' day\n'+state+' period\nref: '+ref, xy=(0.5, 0.5), va='center', ha='center', xycoords='axes fraction', fontsize=11,fontweight='bold')

for ax in axes[[0,-1],:].flatten():
	ax.outline_patch.set_edgecolor('white')
cbar_ax=fig.add_axes([0.1,0.08,0.8,0.2]); cbar_ax.axis('off');
cb=fig.colorbar(im,orientation='horizontal',label='relative bias in exceedance probability [%]',ax=cbar_ax)
tick_locator = matplotlib.ticker.MaxNLocator(nbins=7)
cb.locator = tick_locator
cb.update_ticks()


#plt.suptitle('ensemble mean difference +2$^\circ$C vs 2006-2015', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/validation_exceeProb_maps.png',dpi=300)


#sdasd
