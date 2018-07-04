import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
from statsmodels.sandbox.stats import multicomp

os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence')

summary={}
for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	summary[model]=da.read_nc('data/'+model+'/'+model+'_diff_JJA-warm_1x1.nc')
data=da.DimArray(axes=[summary.keys(),summary[model].keys(),summary[model].lat,summary[model].lon],dims=['model','stat','lat','lon'])
for model in summary.keys():
	for stat in summary[model].keys():
		data[model,stat]=summary[model][stat]

data=da.DimArray(np.roll(data,180,axis=-1),axes=[summary.keys(),summary[model].keys(),summary[model].lat,np.roll(data.lon,180)],dims=['model','stat','lat','lon'])
data.lon[data.lon>180]-=360


# ------------------- changes
plt.close('all')
plate_carree = ccrs.PlateCarree()
fig,axes = plt.subplots(nrows=4,ncols=1,figsize=(10,6),subplot_kw={'projection': plate_carree},gridspec_kw = {'height_ratios':[3,1,3,1]})
for ax in axes[::2]:
	ax.set_global();	ax.coastlines(edgecolor='black');	ax.axis('off');	ax.set_extent([-180,180,20,80],crs=plate_carree)
for ax in axes[1::2]:
	ax.outline_patch.set_edgecolor('white');	ax.axis('off')

xx,yy=data.lon.copy(),data.lat.copy()
x_step,y_step=np.diff(xx,1).mean(),np.diff(yy,1).mean()
xx=np.append(xx-x_step*0.5,xx[-1]+x_step*0.5)
yy=np.append(yy-y_step*0.5,yy[-1]+y_step*0.5)
lons,lats=np.meshgrid(xx,yy)

to_plot=np.nanmean(data[:,'mean_pers',:,:],axis=0)
im=axes[0].pcolormesh(lons,lats,to_plot,vmin=-0.2,vmax=0.2,cmap=plt.cm.PiYG_r);
agreement=np.sum(np.sign(data[:,'mean_pers',:,:].values)==np.sign(to_plot),axis=0)
agreement[np.isfinite(to_plot)==False]=4
stip = axes[0].contourf(data.lon,data.lat, agreement, levels=[0, 3, 4],colors='none', hatches=['/////',None])
cbar_ax=fig.add_axes([0,0.6,1,0.25]);	cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)

to_plot=np.nanmean(data[:,'95th_pers',:,:],axis=0)
im=axes[2].pcolormesh(lons,lats,to_plot,vmin=-1,vmax=1,cmap=plt.cm.PiYG_r);
agreement=np.sum(np.sign(data[:,'95th_pers',:,:].values)==np.sign(to_plot),axis=0)
agreement[np.isfinite(to_plot)==False]=4
stip = axes[2].contourf(data.lon,data.lat, agreement, levels=[0, 3, 4],colors='none', hatches=['/////',None])
cbar_ax=fig.add_axes([0,0.1,1,0.25]);	cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='95th percentile of persistence [days]',ax=cbar_ax)

plt.suptitle('Changes in JJA warm persistence', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/Figure2.png',dpi=300)
