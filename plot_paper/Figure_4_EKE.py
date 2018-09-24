import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
from statsmodels.sandbox.stats import multicomp
import matplotlib.pylab as plt
import matplotlib
import cartopy.crs as ccrs
import cartopy
import seaborn as sns
sns.set()
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

summary={}
for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	summary[model]=da.read_nc('data/EKE/EKE_diff_2vshist_'+model+'_monClim_1x1.nc')['EKE'].squeeze()
data=da.DimArray(axes=[summary.keys(),range(1,13),summary[model].lat,summary[model].lon],dims=['model','month','lat','lon'])
for model in summary.keys():
	data[model]=summary[model]

data=da.DimArray(np.roll(data,180,axis=-1),axes=[summary.keys(),range(1,13),data.lat,np.roll(data.lon,180)],dims=['model','month','lat','lon'])
data.lon[data.lon>180]-=360

plt.close('all')
fig,axes = plt.subplots(nrows=2,ncols=1,figsize=(10,3),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)},gridspec_kw = {'height_ratios':[3,1]})
for ax in axes[::2]:
	ax.set_global();	ax.coastlines(edgecolor='black');	ax.axis('off');	ax.set_extent([-180,180,20,80],crs=ccrs.PlateCarree())
for ax in axes[1::2]:
	ax.outline_patch.set_edgecolor('white');	ax.axis('off')

xx,yy=data.lon.copy(),data.lat.copy()
x_step,y_step=np.diff(xx,1).mean(),np.diff(yy,1).mean()
xx=np.append(xx-x_step*0.5,xx[-1]+x_step*0.5)
yy=np.append(yy-y_step*0.5,yy[-1]+y_step*0.5)
lons,lats=np.meshgrid(xx,yy)

to_plot=np.nanmean(data[:,6:9,:,:],axis=(0,1))
im=axes[0].pcolormesh(lons,lats,to_plot,vmin=-1,vmax=1,cmap=cmap, transform=ccrs.PlateCarree());
agreement=np.sum(np.sign(np.nanmean(data[:,6:9,:,:],axis=1))==np.sign(to_plot),axis=0)
agreement[np.isfinite(to_plot)==False]=4
stip = axes[0].contourf(data.lon,data.lat, agreement, levels=[0, 3, 4],colors='none', hatches=['/////',None], transform=ccrs.PlateCarree())
cbar_ax=fig.add_axes([0,0.2,1,0.5]);	cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='eddy kinetic energy [$m^2s^{-2}$]',ax=cbar_ax)

plt.suptitle('Changes in EKE in JJA', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/paper/Figure_4.png',dpi=300)
