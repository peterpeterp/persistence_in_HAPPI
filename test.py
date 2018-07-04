import seaborn as sns

import matplotlib.pylab as plt
from matplotlib.path import Path
import matplotlib
from matplotlib.collections import PatchCollection

import numpy as np

import cartopy.crs as ccrs
import cartopy

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')


# settings for big plot image
ratio=0.0
plt.close('all')
projection=ccrs.Robinson(central_longitude=167, globe=None)
fig=plt.figure(figsize=(13,6))
ax_map=fig.add_axes([0,0,1,1],projection=projection)
ax_map.set_global()
ax_map.coastlines()
# ax_map.set_xlim((-180,180))
# ax_map.set_ylim((20,80))
ax_map.axis('off')
ax_map.outline_patch.set_edgecolor('white')
ratio=0.0
ax_map.set_extent([-33, 180, 20, 80], crs=ccrs.PlateCarree())
plt.savefig('plots/test.png')
