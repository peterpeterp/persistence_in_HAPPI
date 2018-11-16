import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import matplotlib.pylab as plt
import matplotlib
import dimarray as da
from statsmodels.sandbox.stats import multicomp
import seaborn as sns
sns.set()
import cartopy.crs as ccrs
import cartopy

cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

if 'exceedanceProb' not in globals():
	exceedanceProb={}
	for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
		exceedanceProb[model]=da.read_nc('data/'+model+'/'+model+'_EsceedanceProb_gridded_1x1.nc')

lat,lon = exceedanceProb[model].lat,exceedanceProb[model].lon
lon=np.roll(lon,180)

season='JJA'

color_range={'warm':{14:(-15,15),21:(-15,15)},
			'dry':{14:(-30,30),21:(-30,30)},
			'dry-warm':{14:(-30,30),21:(-30,30)},
			'5mm':{3:(-30,30),7:(-30,30)},
			'10mm':{3:(-30,30),5:(-30,30)},
			}

# ------------------- cold-warm mean
plt.close('all')
fig,axes = plt.subplots(nrows=5,ncols=1,figsize=(4,6),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[4,4,4,4,4]})

for ax in axes[:-1].flatten():
	ax.coastlines(edgecolor='black')
	ax.set_extent([-180,180,0,80],crs=ccrs.PlateCarree())

for model,ax in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],axes[:].flatten()):

	change_dry = (exceedanceProb[model]['*'.join(['Plus20-Future',season,'dry',str(7)])] - exceedanceProb[model]['*'.join(['All-Hist',season,'dry',str(7)])]) / exceedanceProb[model]['*'.join(['All-Hist',season,'dry',str(7)])] * 100
	change_wet = (exceedanceProb[model]['*'.join(['Plus20-Future',season,'5mm',str(7)])] - exceedanceProb[model]['*'.join(['All-Hist',season,'5mm',str(7)])]) / exceedanceProb[model]['*'.join(['All-Hist',season,'5mm',str(7)])] * 100
	change_warm = (exceedanceProb[model]['*'.join(['Plus20-Future',season,'warm',str(7)])] - exceedanceProb[model]['*'.join(['All-Hist',season,'warm',str(7)])]) / exceedanceProb[model]['*'.join(['All-Hist',season,'warm',str(7)])] * 100

	aggree = np.sign(change_dry) + np.sign(change_wet)
	im__=ax.contourf(np.roll(lon,180,axis=-1),lat,aggree,levels=[-3,-1.5,1.5,3],colors=['#00FA9A','white','#CD1076'], transform=ccrs.PlateCarree());

	aggree = np.sign(change_dry) + np.sign(change_wet) + np.sign(change_warm)
	im__=ax.contourf(np.roll(lon,180,axis=-1),lat,aggree,levels=[2.5,3.5], colors=['#FF6A6A'], transform=ccrs.PlateCarree());

	ax.annotate(model, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')

axes[-1].outline_patch.set_edgecolor('white')
legend_elements=[]
legend_elements.append(Patch(facecolor='#CD1076', label='$\uparrow$ dry & $\uparrow$ rainy'))
legend_elements.append(Patch(facecolor='#FF6A6A', label='$\uparrow$ dry & $\uparrow$ rainy & $\uparrow$ warm'))
# legend_elements.append(Patch(facecolor='yellow', label='$\downarrow$ dry & $\uparrow$ rainy OR $\uparrow$ dry & $\downarrow$ rainy'))
legend_elements.append(Patch(facecolor='#00FA9A', label='$\downarrow$ dry & $\downarrow$ rainy'))
axes[-1].legend(handles=legend_elements, fontsize=8)

#plt.suptitle('ensemble mean difference +2$^\circ$C vs 2006-2015', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/paper/map_exceedanceProb_changes_single.png',dpi=300)


#sdasd
