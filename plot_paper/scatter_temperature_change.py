import os,sys,glob,time,collections,gc,pickle
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
from statsmodels.sandbox.stats import multicomp
import matplotlib.pylab as plt
import matplotlib
import cartopy.crs as ccrs
import cartopy
import seaborn as sns
from shapely.geometry.polygon import Polygon
sns.set()
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

temp = da.read_nc('data/tas_summerStat_srex.nc')

EKE = da.read_nc('data/EKE_summerMean_srex.nc')['EKE']
pers = da.read_nc('data/JJA_summary_srex.nc')['exceed_prob']

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()
srex['NHml']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}
for region in srex.keys():
	srex[region]['av_lat']=Polygon(srex[region]['points']).centroid.xy[1][0]

regions = ['ENA','CAS','NHml','NAS','CAM','CNA','NEU','WAS','TIB','CGI','MED','WNA','ALA','CEU','EAS']

plt.close('all')
fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(5,4))
for region in regions:
	y = np.array(np.nanmean( temp['mean_temp'][:,'Plus20-Future',region,'14'].flatten() - temp['mean_temp'][:,'All-Hist',region,'14'].flatten() ))
	x = np.array(np.nanmean( temp['seasMean'][:,'Plus20-Future',region].flatten()-temp['seasMean'][:,'All-Hist',region].flatten() ))
	plt.scatter(x,y, marker = 'v', c = srex[region]['av_lat'], cmap='viridis',vmin=20,vmax=70)
	plt.text(x,y,region,fontsize=6)

ax.axvline(x=0,c='k')
ax.axhline(y=0,c='k')
ax.plot([0,3],[0,3])

ax.set_xlim(1,1.8)
ax.set_ylim(1,1.8)

ax.set_ylabel('change in mean temperature of \nperiods longer than 2 weeks [$^\circ$C]')
ax.set_xlabel('change in seasonal temperature [$^\circ$C]')
# plt.colorbar(im, ax=ax,label='central latitude [deg]')
fig.tight_layout()
plt.savefig('plots/paper/scatter_temperature_change_single.png',dpi=300)

# plt.close('all')
# fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(6,4))
# for region in regions:
# 	y = np.array(np.nanmean( temp['mean_temp'][:,'All-Hist',region,'14'].flatten() - temp['mean_temp'][:,'All-Hist',region,'7'].flatten()))
# 	x = np.array(np.nanmean( temp['mean_temp'][:,'Plus20-Future',region,'14'].flatten() - temp['mean_temp'][:,'Plus20-Future',region,'7'].flatten()))
# 	plt.scatter(x,y, marker = 'v', c = srex[region]['av_lat'], cmap='viridis',vmin=20,vmax=70)
# 	plt.text(x,y,region,fontsize=6)
#
# # ax.axvline(x=0,c='k')
# # ax.axhline(y=0,c='k')
# # ax.plot([0,3],[0,3])
# #
# # ax.set_xlim(1,1.8)
# # ax.set_ylim(1,1.8)
#
# ax.set_ylabel('change in mean temperature of periods longer than 2 weeks [$^\circ$C]')
# ax.set_xlabel('change in seasonal temperature [$^\circ$C]')
# plt.colorbar(im, ax=ax,label='central latitude [deg]')
# fig.tight_layout()
# plt.savefig('plots/paper/Figure_temp_scatter___.png',dpi=300)
