import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import matplotlib.pylab as plt
import matplotlib
import dimarray as da
from statsmodels.sandbox.stats import multicomp
import seaborn as sns
sns.set()


cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", sns.color_palette("cubehelix", 8)[::-1])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

sum_meanQu={}
sum_ks={}
for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	sum_meanQu[model]=da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc')['SummaryMeanQu']
	sum_ks[model]=da.read_nc('data/'+model+'/'+model+'_SummaryKS.nc')['SummaryKS']

sum_meanQu['HadGHCND']=da.read_nc('data/HadGHCND/HadGHCND_SummaryMeanQu.nc')['SummaryMeanQu']
sum_ks['HadGHCND']=da.read_nc('data/HadGHCND/HadGHCND_SummaryFit.nc')['SummaryFit']

# print stats
mean=0
for dataset in ['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	tmp=sum_meanQu[dataset]
	JJA=(tmp['All-Hist']['JJA']['warm']['mean']+tmp['All-Hist']['JJA']['cold']['mean'])*0.5
	DJF=(tmp['All-Hist']['DJF']['warm']['mean']+tmp['All-Hist']['DJF']['cold']['mean'])*0.5
	print(dataset,np.nanmean(DJF[23:66,:])-np.nanmean(JJA[23:66,:]))
	if dataset!='HadGHCND':
		mean+=np.nanmean(DJF[23:66,:])-np.nanmean(JJA[23:66,:])
print('ens-mean',mean/4.)

# ------------------- cold-warm mean
plt.close('all')
plate_carree = ccrs.PlateCarree()
asp=0.8
fig,axes = plt.subplots(nrows=6,ncols=2,figsize=(10*asp,10),subplot_kw={'projection': plate_carree},gridspec_kw = {'height_ratios':[3,3,3,3,3,1]})
for season,col in zip(['JJA','DJF'],[0,1]):
	for dataset,ax in zip(['HadGHCND','MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],axes[:5,col]):
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
		to_plot=(tmp['All-Hist'][season]['warm']['mean']+tmp['All-Hist'][season]['cold']['mean'])*0.5
		im=ax.pcolormesh(lons,lats,to_plot,vmin=3,vmax=7,cmap=cmap);
		ax.annotate(season+'\n'+dataset, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')

for ax in axes[5,:]:
	ax.outline_patch.set_edgecolor('white')

cbar_ax=fig.add_axes([0,0.05,1,0.1])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)

#plt.suptitle('mean persistence', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/paper/FigureSI1_meanClim.png',dpi=300)
