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
sns.set_style("whitegrid")
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

EKE = da.read_nc('data/EKE_summerMean_srex.nc')['EKE']
pers = da.read_nc('data/JJA_summary_srex.nc')['exceed_prob']

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()
srex['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}
for region in srex.keys():
	srex[region]['av_lat']=Polygon(srex[region]['points']).centroid.xy[1][0]

# colors=['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']

regions = ['ENA','CAS','mid-lat','NAS','CAM','CNA','NEU','WAS','TIB','CGI','MED','WNA','ALA','CEU','EAS']
colors=sns.color_palette("cubehelix", 15)[::-1]

regions = np.array(regions)[np.argsort([47.5 - np.abs(srex[region]['av_lat'] - 47.5 ) for region in regions])]

plt.close('all')
fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(5,4))
for region,color in zip(regions,colors):
	for style,state,marker,length in zip(['tas','pr','cpd','pr'],['warm','dry','dry-warm','5mm'],['*','^','s','v'],['14','14','14','7']):
		styleState = style+'_'+state

		if region == 'mid-lat':
			x = np.array([np.nanmean( (EKE[:,'Plus20-Future','NHml']-EKE[:,'All-Hist','NHml'] ) / EKE[:,'All-Hist','NHml'])]) * 100
		else:
			x = np.array([np.nanmean( (EKE[:,'Plus20-Future',region]-EKE[:,'All-Hist',region] ) / EKE[:,'All-Hist',region])]) * 100

		y = np.array([np.nanmean( (pers[:,'Plus20-Future',region,styleState,length]-pers[:,'All-Hist',region,styleState,length] ) / pers[:,'All-Hist',region,styleState,length])]) * 100
		z = (47 - np.abs(srex[region]['av_lat'] - 47.5 ) ) **2 /40.

		plt.scatter(x,y, marker = marker, c = color)#, s=z)

ax.set_ylim((-10,40))
ax.set_xlim((-4.5,2))
ax.axvline(x=0,c='k')
ax.axhline(y=0,c='k')
ax.plot([-50,50],[50,-50],'k--')

ax.set_ylabel('relative change in the probability of \ndry-warm periods exceeding 14 days [%]')
ax.set_xlabel('change in EKE [%]')

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rainy'}

legend_elements=[]
for style,state,marker,length in zip(['tas','pr','cpd','pr'],['warm','dry','dry-warm','5mm'],['*','^','s','v'],['14','14','14','7']):
	legend_elements.append(Line2D([0], [0], color='k', linestyle='',marker=marker, label=length+'-day '+legend_dict[state]))
legend_elements.append(Line2D([0], [0], color='w', linestyle='',marker=marker, label=''))
for region,color in zip(regions,colors):
	legend_elements.append(Line2D([0], [0], color=color, linestyle='',marker='o', label=region))
plt.legend(loc='upper right', handles=legend_elements, fontsize=6, ncol=4, frameon=True, facecolor='w', framealpha=1)



fig.tight_layout()
plt.savefig('plots/paper/scatter_EKE_pers_single.png',dpi=300)
