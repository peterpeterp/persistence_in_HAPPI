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

sum_meanQu={}
sum_ks={}
for style in ['tas','pr','cpd']:
	sum_meanQu[style]={}
	for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
		sum_meanQu[style][model]=da.read_nc('data/'+model+'/'+style+'_'+model+'_SummaryMeanQu.nc')['SummaryMeanQu']
		#sum_ks[model]=da.read_nc('data/'+model+'/'+model+'_SummaryKS.nc')['SummaryKS']

season='JJA'

# ------------------- cold-warm mean
for style,state in zip(['tas','tas','pr','pr','cpd','cpd'],['warm','cold','dry','wet','dry-warm','wet-cold']):
	plt.close('all')
	asp=0.5
	fig,axes = plt.subplots(nrows=5,ncols=2,figsize=(10,6),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)},gridspec_kw = {'height_ratios':[3,3,3,3,1]})

	for ax in axes[:4,:].flatten():
		ax.coastlines(edgecolor='black')
		ax.set_extent([-180,180,0,80],crs=ccrs.PlateCarree())

	for ax in axes[4,:]:
		ax.outline_patch.set_edgecolor('white')

	for dataset,row in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
		for stat,ax,crange,col in zip(['mean','qu_95'],axes[row,:],[[-0.2,0.2],[-0.5,0.5]],range(2)):
			tmp=sum_meanQu[style][dataset]
			to_plot=(tmp['Plus20-Future'][season][state][stat]-tmp['All-Hist'][season][state][stat])
			im=ax.pcolormesh(tmp.lon,tmp.lat,to_plot,vmin=crange[0],vmax=crange[1],cmap=plt.cm.PiYG_r,transform=ccrs.PlateCarree());
			ax.annotate(stat+'\n'+dataset, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')

			if row==3:
				cbar_ax=fig.add_axes([0.5*col,0.08,0.5,0.2])
				cbar_ax.axis('off')
				cb=fig.colorbar(im,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)

	#plt.suptitle('mean persistence', fontweight='bold')
	fig.tight_layout()
	plt.savefig('plots/paper/FigureSI1_change_'+state+'.png',dpi=300)
