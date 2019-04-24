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

pers = da.read_nc('data/EOBS/EOBS_SummaryMeanQu.nc')['SummaryMeanQu']['All-Hist','JJA','5mm','qu_95'].flatten()
tas = da.read_nc('data/EOBS/tg_0.50deg_reg_JJA.nc')['tg'].flatten()
pr = da.read_nc('data/EOBS/rr_0.50deg_reg_JJA.nc')['rr'].flatten()


plt.close('all')
fig,axes = plt.subplots(ncols=3, figsize=(6,4), gridspec_kw = {'width_ratios':[4,4,1]})
ax = axes[0]
im = ax.scatter(pr, tas, c=pers, cmap=hawaii_map, alpha=0.5)
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
			z.append(np.nanmean(pers.values[points]))
ax.scatter(x,y, c=z, cmap=hawaii_map)
ax.set_ylabel('tas')
ax.set_xlabel('pr')

ax = axes[2]
ax.axis('off')
cbar_ax=fig.add_axes([0.65,0.1,0.2,0.8])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='vertical',ax=cbar_ax) #95th percentile\n persistence [days]
cb.set_label(label='Mean rain persistence [days]', fontsize=9)

plt.tight_layout()
plt.savefig('plots/EOBS_scatter.pdf')

#
