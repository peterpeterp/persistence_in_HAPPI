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

EKE = da.read_nc('data/EKE_summerMean_srex.nc')['EKE']
pers = da.read_nc('data/JJA_summary_srex.nc')['exceed_prob']

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()
srex['NHml']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}
for region in srex.keys():
	srex[region]['av_lat']=Polygon(srex[region]['points']).centroid.xy[1][0]

regions = ['ENA','CAS','NHml','NAS','CAM','CNA','NEU','WAS','TIB','CGI','MED','WNA','ALA','CEU','EAS']

plt.close('all')
fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(6,4))
for styleState,marker in zip(['cpd_dry-warm'],['*']):
	for region in regions:
		x = np.array([np.nanmean( (EKE[:,'Plus20-Future',region]-EKE[:,'All-Hist',region] ) / EKE[:,'All-Hist',region])]) * 100
		y = np.array([np.nanmean( (pers[:,'Plus20-Future',region,styleState,'14']-pers[:,'All-Hist',region,styleState,'14'] ) / pers[:,'All-Hist',region,styleState,'14'])]) * 100
		im=ax.scatter(x,y, marker = marker, c = [srex[region]['av_lat']], cmap='viridis',vmin=20,vmax=70)
		ax.text(x,y,region,fontsize=8)

ax.axvline(x=0,c='k')
ax.axhline(y=0,c='k')

ax.set_ylabel('relative change in the probability of \ndry-warm periods exceeding 14 days [%]')
ax.set_xlabel('change in EKE [%]')
plt.colorbar(im, ax=ax,label='central latitude [deg]')
fig.tight_layout()
plt.savefig('plots/paper/Figure_EKE_scatter.png',dpi=300)


plt.close('all')
fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(6,4))
for model,marker in zip(EKE.model,['v','^','o','s']):
	for region in regions:
		x = ( EKE[model,'Plus20-Future',region].flatten()-EKE[model,'All-Hist',region].flatten() ) / EKE[model,'All-Hist',region].flatten() * 100
		y = ( pers[model,'Plus20-Future',region,'cpd_dry-warm','14'].flatten()-pers[model,'All-Hist',region,'cpd_dry-warm','14'].flatten() ) / pers[model,'All-Hist',region,'cpd_dry-warm','14'].flatten() * 100
		plt.scatter(x,y, marker = marker, c = [srex[region]['av_lat']], cmap='viridis',vmin=20,vmax=70)
		plt.text(x,y,region,fontsize=6)

ax.axvline(x=0,c='k')
ax.axhline(y=0,c='k')

for model,marker in zip(EKE.model,['v','^','o','s']):
    plt.scatter([], [], c='k',label=model, marker=marker)
plt.legend(scatterpoints=1, frameon=False, labelspacing=1, title='Models')


ax.set_ylabel('relative change in the probability of \ndry-warm periods exceeding 14 days [%]')
ax.set_xlabel('change in EKE [%]')
plt.colorbar(im, ax=ax,label='central latitude [deg]')
fig.tight_layout()
plt.savefig('plots/paper/Figure_EKE_scatter__.png',dpi=300)





#
