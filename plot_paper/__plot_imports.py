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
	'EKE':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/EKE.png')),
	# 'water':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/drop.png')),
	# 'dry':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/plumbing.png')),
	# 'drought':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/nature.png')),
	'increase':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/increase.png')),
	'decrease':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/decrease.png')),
	'SPI3':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/soil-moisture.png')),
	'rain':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/rain.png')),
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








# def plot_model_column(ax,x,var,signi=None,label=' ',c_range=(-0.3,0.3), plot_type='normal', cmap='RdBu', signi_lvl=0.05):
# 	patches = []
# 	colors = []
# 	ax.plot([x-0.5,x-0.5],[-2,15],color='k')
# 	ax.text(x,13.7,label,ha='center',va='bottom',rotation=90,fontsize=8,weight="bold")
#
# 	if c_range == 'maxabs':
# 		maxabs = np.nanmax(np.abs(np.nanpercentile(var,[0,100])))
# 		c_range = [-maxabs,maxabs]
#
# 	result = []
# 	for region,y in regions.items():
# 		for model in model_shifts.keys():
# 			x_shi,y_shi = model_shifts[model]
#
# 			if np.isfinite(var[model,region]):
# 				if plot_type=='normal':
# 					polygon = Polygon([(x+x_shi-x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi+y_wi),(x+x_shi-x_wi,y+y_shi+y_wi)], True)
# 					patches.append(polygon)
# 					colors.append(var[model,region])
# 				if plot_type=='upper':
# 					polygon = Polygon([(x+x_shi-x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi+y_wi),(x+x_shi-x_wi,y+y_shi+y_wi)], True)
# 					patches.append(polygon)
# 					colors.append(var[model,region])
# 				if plot_type=='bool':
# 					style = bool_styles[np.sign(var[model,region])]
# 					ax.plot(x+x_shi,y+y_shi, marker=style['m'], color=style['c'])
#
# 				if signi is not None:
# 					if signi[model,region] < signi_lvl:
# 						ax.plot(x+x_shi*1.2,y+y_shi*1.2, marker='.', color='k')
#
# 	if plot_type != 'bool':
# 		if c_range is None:
# 			c_range = [np.min(var),np.max(var)]
# 		y= -0.3
# 		for x_shi,val in zip([-0.33,0,+0.33],[c_range[0]*2/3.,np.mean(c_range),c_range[1]*2/3.]):
# 			polygon = Polygon([(x+x_shi-0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi+y_wi),(x+x_shi-0.33*0.5,y+y_shi+y_wi)], True)
# 			patches.append(polygon)
# 			colors.append(val)
# 			ax.text(x+x_shi,-1.3,round(val,02),ha='center',va='top',rotation=-90,fontsize=8,weight="bold")
#
# 	p = PatchCollection(patches, cmap=cmap, alpha=1)
# 	p.set_array(np.array(colors))
# 	p.set_clim(c_range)
# 	im = ax.add_collection(p)
#
# 	return c_range
#
# def plot_obs_column(ax,x,var,masks,pval=None,c_range=(-0.3,0.3), label=' ', x_shi=0 ,y_shi=0, cmap='RdBu'):
# 	patches = []
# 	colors = []
# 	for region,y in regions.items():
# 		if region in masks.keys():
# 			mask = masks[region].copy()
# 			if mask.shape != var['JJA'].shape:
# 				mask = mask.T
# 			cor = np.array(var['JJA'].values * mask.values).flatten()
# 			relevant_cells = np.where((mask.flatten()>0) & (np.isfinite(cor)))[0]
# 			cor = cor[relevant_cells]
#
# 			patches.append(plt.Circle((x, y), 0.25))
# 			colors.append(np.nansum(cor))
#
# 			# homogenety = np.sum( np.sign(cor) == np.sign(np.nansum(cor)) ) / float(cor.shape[0])
# 			# if homogenety >= 0.9:
# 			# 	ax.plot([x],[y],'*k')
#
# 			mask[mask>0] = 1
# 			pval_ = np.array(pval['JJA'].values * mask.values).flatten()
# 			signi = np.sum( (np.sign(cor) == np.sign(np.nansum(cor))) & (pval_[relevant_cells] < 0.05) ) / float(cor.shape[0])
# 			if signi >= 0.5:
# 				ax.plot([x],[y],'*k')
#
#
# 	p = PatchCollection(patches, cmap=cmap, edgecolor='k', alpha=1)
# 	p.set_array(np.array(colors))
# 	p.set_clim(c_range)
# 	ax.add_collection(p)
#
# 	return ax










#
