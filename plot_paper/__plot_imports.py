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
from matplotlib.cbook import get_sample_data
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import matplotlib
from matplotlib.backends.backend_pdf import PdfPages

import cartopy.crs as ccrs
import cartopy
import seaborn as sns
import shapely
sns.set()
sns.set_style("whitegrid")




icon_dict = {
	'EKE':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/storm.png')),
	# 'water':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/drop.png')),
	# 'dry':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/plumbing.png')),
	# 'drought':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/nature.png')),
	1:plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/increase.png')),
	-1:plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/decrease.png')),
	'SPI3':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/rain.png')),
	# 'no_rain':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/no_rain.png')),
}

def imscatter(x, y, image, ax=None, zoom=1):
    if ax is None:
        ax = plt.gca()
    try:
        image = plt.imread(image)
    except TypeError:
        # Likely already an array...
        pass
    im = OffsetImage(image, zoom=zoom)
    x, y = np.atleast_1d(x, y)
    artists = []
    for x0, y0 in zip(x, y):
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    ax.update_datalim(np.column_stack([x, y]))
    # ax.autoscale()
    return artists



















#
