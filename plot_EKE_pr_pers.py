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
	sum_meanQu[model]=da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc')['SummaryMeanQu']
	sum_ks[model]=da.read_nc('data/'+model+'/'+model+'_SummaryKS.nc')['SummaryKS']

# print stats
mean=0
for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	tmp=sum_meanQu[dataset]
	JJA=(tmp['All-Hist']['JJA']['warm']['mean']+tmp['All-Hist']['JJA']['cold']['mean'])*0.5
	DJF=(tmp['All-Hist']['DJF']['warm']['mean']+tmp['All-Hist']['DJF']['cold']['mean'])*0.5
	print(dataset,np.nanmean(DJF[23:66,:])-np.nanmean(JJA[23:66,:]))
	if dataset!='HadGHCND':
		mean+=np.nanmean(DJF[23:66,:])-np.nanmean(JJA[23:66,:])
print('ens-mean',mean/4.)


# ------------------- changes
plt.close('all')
plate_carree = ccrs.PlateCarree()
fig,axes = plt.subplots(nrows=5,ncols=3,figsize=(8,8),subplot_kw={'projection': plate_carree},gridspec_kw = {'height_ratios':[3,3,3,3,1]})
for season,col in zip(['JJA','DJF'],[0,1]):
	for dataset,ax in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],axes[:4,col]):
		ax.set_global()
		ax.coastlines(edgecolor='black')
		ax.axis('off')
		ax.set_extent([-180,180,-66,80],crs=plate_carree)
		tmp=sum_meanQu[dataset]

		xx,yy=tmp.lon.copy(),tmp.lat.copy()
		x_step,y_step=np.diff(xx,1).mean(),np.diff(yy,1).mean()
		xx=np.append(xx-x_step*0.5,xx[-1]+x_step*0.5)
		yy=np.append(yy-y_step*0.5,yy[-1]+y_step*0.5)
		lons,lats=np.meshgrid(xx,yy)
		to_plot_warm=(tmp['Plus20-Future'][season]['warm']['mean']-tmp['All-Hist'][season]['warm']['mean'])*0.5
		to_plot_cold=(tmp['Plus20-Future'][season]['cold']['mean']-tmp['All-Hist'][season]['cold']['mean'])*0.5
		to_plot=(to_plot_warm+to_plot_cold)*0.5
		im=ax.pcolormesh(lons,lats,to_plot,vmin=-0.2,vmax=0.2,cmap=plt.cm.PiYG_r);

		significance=np.asarray(sum_ks[dataset]['Plus20-Future'][season]['stateInd']['KS_vs_All-Hist'].copy())
		significance[np.isnan(significance)]=1
		significance_=multicomp.multipletests(significance.reshape((len(tmp.lat)*len(tmp.lon))), method='fdr_bh')[1].reshape((len(tmp.lat),len(tmp.lon)))
		stip = ax.contourf(tmp.lon, tmp.lat, significance_, levels=[-1, 0.1, 1],colors='none', hatches=['.....',None])

		ax.annotate(season+' '+'\n'+dataset, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')

for ax in axes[4,:]:
	ax.outline_patch.set_edgecolor('white')

cbar_ax=fig.add_axes([0,0.07,1,0.15])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='changes in mean persistence [days]',ax=cbar_ax)
cbar_ax.tick_params(labelsize=9)

#plt.suptitle('mean persistence', fontweight='bold')
fig.tight_layout()
#plt.savefig('plots/diff_map_stateInd.png',dpi=300)
plt.savefig('plots/diff_map_stateInd_fdr_bh.png',dpi=300)
