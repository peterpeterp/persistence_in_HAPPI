import os,sys,glob,time,collections,gc,pickle,textwrap
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
from statsmodels.sandbox.stats import multicomp
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection

import matplotlib
import cartopy.crs as ccrs
import cartopy
import seaborn as sns
import shapely


sys.path.append("/Users/peterpfleiderer/Projects/git-packages/ScientificColourMaps5/hawaii")
from hawaii import *

sns.set()
sns.set_style("whitegrid")

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

pers = da.read_nc('data/EOBS/EOBS_SummaryMeanQu.nc')['SummaryMeanQu']['All-Hist','JJA','5mm','qu_95'].flatten().values
excee = da.read_nc('data/EOBS/EOBS_EsceedanceProb_gridded.nc')['ExceedanceProb']['All-Hist','JJA','5mm',5].flatten().values * 100
tas = da.read_nc('data/EOBS/tg_0.50deg_reg_sea_clim.nc')['tg'].ix[2].flatten().values
pr = da.read_nc('data/EOBS/rr_0.50deg_reg_sea_clim.nc')['rr'].ix[2].flatten().values

# excee.values = (excee.values - np.nanmin(excee)) / (np.nanmax(excee) - np.nanmin(excee))

mask = ~np.isnan(excee) & ~np.isnan(tas) & ~np.isnan(pr)
excee = excee[mask]
tas = tas[mask]
pr = pr[mask]

plt.close('all')
fig,axes = plt.subplots(ncols=4,nrows=3, figsize=(9,5))
axes=axes.flatten()
for iax,pp in enumerate(np.arange(0,4.5,0.5)):
	points = np.where( (pr>pp) & (pr<pp+0.5))[0]
	im = axes[iax].scatter(tas[points], excee[points])
	slope, intercept, r_value, p_value, std_err = stats.linregress(tas[points], excee[points])
	print(slope,excee[points].mean())
	axes[iax].plot(tas[points],intercept+slope*tas[points], c='r')
	axes[iax].set_title('%1.1f < pr < %1.1f' %(pp,pp+0.5))
	axes[iax].set_ylabel('Excee. Prob.')
	axes[iax].set_xlabel('tas')

points = np.where( (pr>pp+0.5))[0]
im = axes[iax+1].scatter(tas[points], excee[points])
slope, intercept, r_value, p_value, std_err = stats.linregress(tas[points], excee[points])
axes[iax+1].plot(tas[points],intercept+slope*tas[points], c='r')
axes[iax+1].set_title('%1.1f < pr < %1.1f' %(pp,pp+0.5))
axes[iax+1].set_ylabel('Excee. Prob.')
axes[iax+1].set_xlabel('tas')
plt.tight_layout()
plt.savefig('plots/EOBS_scatter_multi.pdf')




plt.close('all')
fig,axes = plt.subplots(ncols=3, figsize=(6,4), gridspec_kw = {'width_ratios':[4,4,1]})
ax = axes[0]
im = ax.scatter(pr, tas, c=excee, cmap=hawaii_map, alpha=0.5, vmin=0, vmax=2)
ax.set_ylabel('tas')
ax.set_xlabel('pr')

ax = axes[1]
y,x,z = [],[],[]
for pp in np.arange(0,9,0.1):
	for tt in np.arange(-10,20,1):
		points = np.where( (pr>pp) & (pr<pp+0.1) & (tas>tt) & (tas<tt+0.5) )[0]
		if len(points)>0:
			y.append(tt+0.5)
			x.append(pp+0.05)
			z.append(np.nanmean(excee[points]))
ax.scatter(x,y, c=z, cmap=hawaii_map, vmin=0, vmax=2)
ax.set_ylabel('tas')
ax.set_xlabel('pr')

ax = axes[2]
ax.axis('off')
cbar_ax=fig.add_axes([0.65,0.1,0.2,0.8])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='vertical',ax=cbar_ax) #95th percentile\n persistence [days]
cb.set_label(label='Exceedance Probability of 5 days rain', fontsize=9)

plt.tight_layout()
plt.savefig('plots/EOBS_scatter.pdf')





#
