import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
from statsmodels.sandbox.stats import multicomp

os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence')

sum_meanQu={}
sum_ks={}
for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	sum_meanQu[model]=da.read_nc('data/'+model+'/pr_'+model+'_SummaryMeanQu.nc')['SummaryMeanQu']
	sum_ks[model]=da.read_nc('data/'+model+'/pr_'+model+'_SummaryKS.nc')['SummaryKS']


# ------------------- cold-warm mean
plt.close('all')
plate_carree = ccrs.PlateCarree()
for stat,crange in zip(['mean','qu_95'],[[1,7],[1,15]]):
	fig,axes = plt.subplots(nrows=5,ncols=1,figsize=(10,10),subplot_kw={'projection': plate_carree},gridspec_kw = {'height_ratios':[3,3,3,3,1]})
	for dataset,ax in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],axes[:4]):
		ax.set_global()
		ax.coastlines(edgecolor='black')
		ax.axis('off')
		ax.set_extent([-180,180,20,80],crs=plate_carree)
		tmp=sum_meanQu[dataset]

		xx,yy=tmp.lon.copy(),tmp.lat.copy()
		x_step,y_step=np.diff(xx,1).mean(),np.diff(yy,1).mean()
		xx=np.append(xx-x_step*0.5,xx[-1]+x_step*0.5)
		yy=np.append(yy-y_step*0.5,yy[-1]+y_step*0.5)
		lons,lats=np.meshgrid(xx,yy)
		to_plot=tmp['All-Hist']['JJA']['dry'][stat]
		im=ax.pcolormesh(lons,lats,to_plot,vmin=crange[0],vmax=crange[1],cmap=plt.cm.jet);
		ax.annotate('JJA'+'\n'+dataset, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')

	axes[4].outline_patch.set_edgecolor('white')

	cbar_ax=fig.add_axes([0,0.05,1,0.2])
	cbar_ax.axis('off')
	cb=fig.colorbar(im,orientation='horizontal',label=stat+' persistence [days]',ax=cbar_ax)

	#plt.suptitle('mean persistence', fontweight='bold')
	fig.tight_layout()
	plt.savefig('plots/dry_pers_climatology_'+stat+'.png',dpi=300)
