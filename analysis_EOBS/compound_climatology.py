import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import matplotlib.pyplot as plt
import seaborn as sns
import cartopy.crs as ccrs
import cartopy

sns.set_palette("husl")

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

data_path='data/EOBS/'

# tas_=da.read_nc(data_path+'tas_EOBS_SummaryMeanQu.nc')['SummaryMeanQu']
# pr_=da.read_nc(data_path+'pr_EOBS_SummaryMeanQu.nc')['SummaryMeanQu']
# cpd_=da.read_nc(data_path+'cpd_EOBS_SummaryMeanQu.nc')['SummaryMeanQu']


plt.close()
fig,axes = plt.subplots(nrows=6,ncols=3,figsize=(10,10),subplot_kw={'projection': ccrs.PlateCarree()},gridspec_kw = {'height_ratios':[3,3,1,3,3,1]})

for ax in axes[[0,1,3,4],:].flatten():
	ax.coastlines(edgecolor='black')

for ax in axes[[2,5],:].flatten():
	ax.outline_patch.set_edgecolor('white')

im=axes[0,0].pcolormesh(tas_.lon,tas_.lat,tas_['All-Hist','JJA','warm','mean'],vmin=1,vmax=7,cmap=plt.cm.jet)
axes[0,0].set_title('warm')
im=axes[0,1].pcolormesh(tas_.lon,tas_.lat,cpd_['All-Hist','JJA','dry-warm','mean'],vmin=1,vmax=7,cmap=plt.cm.jet)
axes[0,1].set_title('dry-warm')
im=axes[0,2].pcolormesh(tas_.lon,tas_.lat,pr_['All-Hist','JJA','dry','mean'],vmin=1,vmax=7,cmap=plt.cm.jet)
axes[0,2].set_title('dry')

im=axes[1,0].pcolormesh(tas_.lon,tas_.lat,tas_['All-Hist','JJA','cold','mean'],vmin=1,vmax=7,cmap=plt.cm.jet)
axes[1,0].set_title('cold')
im=axes[1,1].pcolormesh(tas_.lon,tas_.lat,cpd_['All-Hist','JJA','wet-cold','mean'],vmin=1,vmax=7,cmap=plt.cm.jet)
axes[1,1].set_title('wet-cold')
im=axes[1,2].pcolormesh(tas_.lon,tas_.lat,pr_['All-Hist','JJA','wet','mean'],vmin=1,vmax=7,cmap=plt.cm.jet)
axes[1,2].set_title('wet')

cbar_ax=fig.add_axes([0,0.57,1,0.15])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)
cbar_ax.tick_params(labelsize=9)

im=axes[3,0].pcolormesh(tas_.lon,tas_.lat,tas_['All-Hist','JJA','warm','qu_95'],vmin=4,vmax=20,cmap=plt.cm.jet)
axes[3,0].set_title('warm')
im=axes[3,1].pcolormesh(tas_.lon,tas_.lat,cpd_['All-Hist','JJA','dry-warm','qu_95'],vmin=4,vmax=20,cmap=plt.cm.jet)
axes[3,1].set_title('dry-warm')
im=axes[3,2].pcolormesh(tas_.lon,tas_.lat,pr_['All-Hist','JJA','dry','qu_95'],vmin=4,vmax=20,cmap=plt.cm.jet)
axes[3,2].set_title('dry')

im=axes[4,0].pcolormesh(tas_.lon,tas_.lat,tas_['All-Hist','JJA','cold','qu_95'],vmin=4,vmax=20,cmap=plt.cm.jet)
axes[4,0].set_title('cold')
im=axes[4,1].pcolormesh(tas_.lon,tas_.lat,cpd_['All-Hist','JJA','wet-cold','qu_95'],vmin=4,vmax=20,cmap=plt.cm.jet)
axes[4,1].set_title('wet-cold')
im=axes[4,2].pcolormesh(tas_.lon,tas_.lat,pr_['All-Hist','JJA','wet','qu_95'],vmin=4,vmax=20,cmap=plt.cm.jet)
axes[4,2].set_title('wet')

cbar_ax=fig.add_axes([0,0.07,1,0.15])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='95th percentile of persistence [days]',ax=cbar_ax)
cbar_ax.tick_params(labelsize=9)

#plt.suptitle('Moscow 2010')
plt.tight_layout()
plt.savefig('plots/EOBS_compound_climatology.png')
