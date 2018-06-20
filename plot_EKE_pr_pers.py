import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
from statsmodels.sandbox.stats import multicomp
import cartopy.crs as ccrs
import cartopy
import matplotlib
os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence')

sum_meanQu={}
sum_ks={}
for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	sum_meanQu[model]=da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc')['SummaryMeanQu']
	sum_ks[model]=da.read_nc('data/'+model+'/'+model+'_SummaryKS.nc')['SummaryKS']

sum_corEKE={}
sum_corSPI={}
for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	sum_corEKE[model]=da.read_nc('data/'+model+'/corEKE_'+model+'_summary.nc')['corEKE']
	sum_corSPI[model]=da.read_nc('data/'+model+'/corSPI_'+model+'_summary.nc')['corSPI']

sum_EKE={}
sum_SPI={}
sum_pr={}
for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	sum_EKE[model]={}
	sum_SPI[model]={}
	sum_pr[model]={}
	for scenario in ['All-Hist','Plus20-Future']:
		sum_EKE[model][scenario]=da.read_nc('data/EKE/EKE_'+scenario+'_'+model+'_monClim.nc')['EKE']
		sum_SPI[model][scenario]=da.read_nc('data/SPI/SPI_'+model+'_'+scenario+'_monClim.nc')['SPI']
		sum_pr[model][scenario]=da.read_nc('data/pr/pr_'+model+'_'+scenario+'_monClim.nc')['pr']

corr_colors = matplotlib.colors.LinearSegmentedColormap.from_list("", ["cyan","green","white","red","magenta"])
change_colors = matplotlib.colors.LinearSegmentedColormap.from_list("", ["blue","cyan","lightblue","white","plum","magenta","darkmagenta"])

# ------------------- overview for one model
plt.close('all')
plate_carree = ccrs.PlateCarree()
for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	fig,axes = plt.subplots(nrows=2,ncols=3,figsize=(12,6),subplot_kw={'projection': plate_carree},gridspec_kw = {'height_ratios':[3,3]})
	for ax in axes.flatten():
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

	mask=sum_meanQu[dataset]['All-Hist']['JJA']['warm']['mean'].copy()
	mask[np.isfinite(mask)]=1

	im=axes[0,0].pcolormesh(lons,lats,sum_meanQu[dataset]['All-Hist']['JJA']['warm']['mean'],vmin=3,vmax=7,cmap=plt.cm.jet)
	cb=fig.colorbar(im,orientation='horizontal',label='mean persistence [days]',ax=axes[0,0])

	im=axes[0,1].pcolormesh(lons,lats,sum_corEKE[dataset]['All-Hist'][1,1,'corrcoef_mn'],vmin=-0.5,vmax=0.5,cmap=corr_colors)
	cb=fig.colorbar(im,orientation='horizontal',label='correlation persistnce - EKE',ax=axes[0,1])

	im=axes[0,2].pcolormesh(lons,lats,sum_corSPI[dataset]['All-Hist'][1,1,'corrcoef_mn'],vmin=-0.5,vmax=0.5,cmap=corr_colors)
	cb=fig.colorbar(im,orientation='horizontal',label='correlation persistnce - SPI',ax=axes[0,2])

	to_plot=sum_meanQu[dataset]['Plus20-Future']['JJA']['warm']['mean']-sum_meanQu[dataset]['All-Hist']['JJA']['warm']['mean']
	im=axes[1,0].pcolormesh(lons,lats,to_plot,vmin=-0.2,vmax=0.2,cmap=change_colors)
	cb=fig.colorbar(im,orientation='horizontal',label='changes in mean persistence [days]',ax=axes[1,0])

	to_plot=sum_EKE[dataset]['Plus20-Future'].ix[5:8,0,:,:].mean(axis=0)-sum_EKE[dataset]['All-Hist'].ix[5:8,0,:,:].mean(axis=0)
	im=axes[1,1].pcolormesh(lons,lats,to_plot,vmin=-0.5,vmax=0.5,cmap=change_colors)
	cb=fig.colorbar(im,orientation='horizontal',label='changes in EKE [m2s-2]',ax=axes[1,1])

	to_plot=(sum_pr[dataset]['Plus20-Future'].squeeze().ix[3:6,:,:].mean(axis=0)-sum_pr[dataset]['All-Hist'].squeeze().ix[3:6,:,:].mean(axis=0))/sum_pr[dataset]['All-Hist'].squeeze().ix[3:6,:,:].mean(axis=0)*100*mask
	im=axes[1,2].pcolormesh(lons,lats,to_plot,vmin=-10,vmax=10,cmap=change_colors)
	cb=fig.colorbar(im,orientation='horizontal',label='changes in pr Mai April June[%]',ax=axes[1,2])


	#plt.suptitle('mean persistence', fontweight='bold')
	fig.tight_layout()
	#plt.savefig('plots/diff_map_stateInd.png',dpi=300)
	plt.savefig('plots/overview_'+dataset+'.png',dpi=300)



# # print stats
# mean=0
# for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
# 	tmp=sum_meanQu[dataset]
# 	JJA=(tmp['All-Hist']['JJA']['warm']['mean']+tmp['All-Hist']['JJA']['cold']['mean'])*0.5
# 	DJF=(tmp['All-Hist']['DJF']['warm']['mean']+tmp['All-Hist']['DJF']['cold']['mean'])*0.5
# 	print(dataset,np.nanmean(DJF[23:66,:])-np.nanmean(JJA[23:66,:]))
# 	if dataset!='HadGHCND':
# 		mean+=np.nanmean(DJF[23:66,:])-np.nanmean(JJA[23:66,:])
# print('ens-mean',mean/4.)
#

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
