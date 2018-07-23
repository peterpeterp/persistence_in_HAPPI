import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
from statsmodels.sandbox.stats import multicomp

os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence')

summary=da.read_nc('data/'+'HadGHCND'+'/'+'HadGHCND'+'_SummaryMeanQu.nc')['SummaryMeanQu']
ks=da.read_nc('data/'+'HadGHCND'+'/'+'HadGHCND'+'_SummaryKS.nc')['SummaryKS']


# ------------------- changes
plt.close('all')
plate_carree = ccrs.PlateCarree()
fig,axes = plt.subplots(nrows=4,ncols=1,figsize=(10,6),subplot_kw={'projection': plate_carree},gridspec_kw = {'height_ratios':[3,1,3,1]})
for ax in axes[::2]:
	ax.set_global();	ax.coastlines(edgecolor='black');	ax.axis('off');	ax.set_extent([-180,180,20,80],crs=plate_carree)
for ax in axes[1::2]:
	ax.outline_patch.set_edgecolor('white');	ax.axis('off')

xx,yy=summary.lon.copy(),summary.lat.copy()
x_step,y_step=np.diff(xx,1).mean(),np.diff(yy,1).mean()
xx=np.append(xx-x_step*0.5,xx[-1]+x_step*0.5)
yy=np.append(yy-y_step*0.5,yy[-1]+y_step*0.5)
lons,lats=np.meshgrid(xx,yy)

to_plot=summary['1990-2010','JJA','warm','mean']-summary['1954-1974','JJA','warm','mean']
im=axes[0].pcolormesh(lons,lats,to_plot,vmin=-1,vmax=1,cmap=plt.cm.PiYG_r);
# agreement=ks['1990-2010','JJA','warm','KS_vs_1954-1974'].values
# stip = axes[0].contourf(ks.lon,ks.lat, agreement, levels=[0, 0.05, 1],colors='none', hatches=['/////',None])
cbar_ax=fig.add_axes([0,0.6,1,0.25]);	cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)

to_plot=summary['1990-2010','JJA','warm','qu_95']-summary['1954-1974','JJA','warm','qu_95']
im=axes[2].pcolormesh(lons,lats,to_plot,vmin=-3,vmax=3,cmap=plt.cm.PiYG_r);
# agreement=ks['1990-2010','JJA','warm','KS_vs_1954-1974'].values
# agreement[np.isfinite(agreement)==False]=0
# stip = axes[2].contourf(ks.lon,ks.lat, agreement, levels=[0, 0.05, 1],colors='none', hatches=[None,'/////'])
cbar_ax=fig.add_axes([0,0.1,1,0.25]);	cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='95th percentile of persistence [days]',ax=cbar_ax)

plt.suptitle('Changes in JJA warm persistence', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/Had_Figure2.png',dpi=300)
