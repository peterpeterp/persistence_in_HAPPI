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

cmap = {'mean': matplotlib.colors.LinearSegmentedColormap.from_list("", sns.cubehelix_palette(8)),
		'qu_95': matplotlib.colors.LinearSegmentedColormap.from_list("", sns.cubehelix_palette(8, start=.5, rot=-.75))}

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

obs_eobs={}
for style in ['tas','pr','cpd']:
	obs_eobs[style] = da.read_nc('data/EOBS/'+style+'_EOBS_SummaryMeanQu.nc')['SummaryMeanQu']

obs_had={}
for style in ['tas']:
	obs_had[style] = da.read_nc('data/HadGHCND/HadGHCND_SummaryMeanQu.nc')['SummaryMeanQu']

if 'models' not in globals():
	models={}
	for style in ['tas','pr','cpd']:
		models[style]={}
		for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
			models[style][model]=da.read_nc('data/'+model+'/'+style+'_'+model+'_SummaryMeanQu_1x1.nc')


season='JJA'

color_range={'warm':{'mean':(3,7),'qu_95':(5,20)},
			'cold':{'mean':(3,7),'qu_95':(5,20)},
			'dry':{'mean':(3,14),'qu_95':(5,20)},
			'wet':{'mean':(1,4),'qu_95':(2,10)},
			'dry-warm':{'mean':(1,4),'qu_95':(5,14)},
			'wet-cold':{'mean':(1,4),'qu_95':(4,10)},
			}

# ------------------- other
for style,state in zip(['pr','pr','cpd','cpd'],['dry','wet','dry-warm','wet-cold']):

	plt.close('all')
	fig,axes = plt.subplots(nrows=3,ncols=3,figsize=(6,3),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[1,10,10],'width_ratios':[1,3,1]})

	for ax in list(axes[0,:].flatten()) + list(axes[:,-1].flatten()):
		ax.outline_patch.set_edgecolor('white')

	im={}
	for name,data,col in zip(['EOBS','HAPPI'],[obs_eobs,models],range(2)):
		for stat,ax in zip(['mean','qu_95'],axes[1:,col]):
			ax.coastlines(edgecolor='black')
			if name == 'EOBS':
				ax.set_extent([-15,60,10,80],crs=ccrs.PlateCarree())
			else:
				ax.set_extent([-15,345,10,80],crs=ccrs.PlateCarree())

			if name == 'HAPPI':
				ensemble=np.zeros([4,180,360])*np.nan
				for model,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
					ensemble[i,:,:]=models[style][model]['*'.join(['All-Hist',season,state,stat])]
				to_plot=sum_meanQu[style][model]['*'.join(['All-Hist',season,state,stat])].copy()
				to_plot.values=np.roll(np.nanmean(ensemble,axis=0),180,axis=-1)
				to_plot.lon=np.roll(to_plot.lon,180,axis=-1)
			else:
				to_plot=data[style]['All-Hist',season,state,stat]

			ax.annotate(name, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')
			crange=color_range[state][stat]
			im[stat]=ax.pcolormesh(to_plot.lon,to_plot.lat,to_plot ,vmin=crange[0],vmax=crange[1],cmap=cmap[stat],transform=ccrs.PlateCarree());

	cbar_ax=fig.add_axes([0.1,0.55,0.8,0.4])
	cbar_ax.axis('off')
	cb=fig.colorbar(im['mean'],orientation='vertical',label='mean persistence\n [days]',ax=cbar_ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

	cbar_ax=fig.add_axes([0.1,0.1,0.8,0.4])
	cbar_ax.axis('off')
	cb=fig.colorbar(im['qu_95'],orientation='vertical',label='95th percentile\n persistence [days]',ax=cbar_ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

	plt.suptitle(state+' persistence', fontweight='bold')
	fig.tight_layout()
	plt.savefig('plots/paper/FigureSI1_climatology_'+state+'.png',dpi=300)

# warm cold
for style,state in zip(['tas','tas'],['warm','cold']):
	plt.close('all')
	fig,axes = plt.subplots(nrows=3,ncols=4,figsize=(10,3),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[1,10,10],'width_ratios':[3,1,3,1]})

	for ax in list(axes[0,:].flatten()) + list(axes[:,-1].flatten()):
		ax.outline_patch.set_edgecolor('white')

	im={}
	for name,data,col in zip(['HadGHCND','EOBS','HAPPI'],[obs_had,obs_eobs,models],range(3)):
		for stat,ax in zip(['mean','qu_95'],axes[1:,col]):
			ax.coastlines(edgecolor='black')
			if name == 'EOBS':
				ax.set_extent([-15,60,10,80],crs=ccrs.PlateCarree())
			else:
				ax.set_extent([-15,345,10,80],crs=ccrs.PlateCarree())

			if name == 'HAPPI':
				ensemble=np.zeros([4,180,360])*np.nan
				for model,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
					ensemble[i,:,:]=models[style][model]['*'.join(['All-Hist',season,state,stat])]
				to_plot=sum_meanQu[style][model]['*'.join(['All-Hist',season,state,stat])].copy()
				to_plot.values=np.roll(np.nanmean(ensemble,axis=0),180,axis=-1)
				to_plot.lon=np.roll(to_plot.lon,180,axis=-1)
			else:
				to_plot=data[style]['All-Hist',season,state,stat]

			ax.annotate(name, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')
			crange=color_range[state][stat]
			im[stat]=ax.pcolormesh(to_plot.lon,to_plot.lat,to_plot ,vmin=crange[0],vmax=crange[1],cmap=cmap[stat],transform=ccrs.PlateCarree());

	cbar_ax=fig.add_axes([0.2,0.55,0.8,0.4])
	cbar_ax.axis('off')
	cb=fig.colorbar(im['mean'],orientation='vertical',label='mean persistence\n [days]',ax=cbar_ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

	cbar_ax=fig.add_axes([0.2,0.1,0.8,0.4])
	cbar_ax.axis('off')
	cb=fig.colorbar(im['qu_95'],orientation='vertical',label='95th percentile\n persistence [days]',ax=cbar_ax)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

	plt.suptitle(state+' persistence', fontweight='bold')
	fig.tight_layout()
	plt.savefig('plots/paper/FigureSI1_climatology_'+state+'.png',dpi=300)
