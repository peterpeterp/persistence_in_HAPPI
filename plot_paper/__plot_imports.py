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

plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

icon_dict = {
	'avoided':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/avoided.png')),'scale':1},
	'mitigated':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/mitigated.png')),'scale':1},
	'increase_red':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/increase_red.png')),'scale':1},
	'decrease_red':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/decrease_red.png')),'scale':1},
	'EKE':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/EKE.png')),'scale':1},
	# 'water':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/drop.png')),'scale':1},
	# 'dry':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/plumbing.png')),'scale':1},
	# 'drought':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/nature.png')),'scale':1},
	'increase':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/increase.png')),'scale':1},
	'decrease':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/decrease.png')),'scale':1},
	'SPI3':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/SPI3.png')),'scale':1.5},
	'rain':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/rain.png')),'scale':1},
	# 'no_rain':{'icon':plt.imread(get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/no_rain.png')),'scale':1},
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

NH_regs={'ALA':{'color':'darkgreen','pos_off':(+0,+3),'summer':'JJA','winter':'DJF'},
		'WNA':{'color':'darkblue','pos_off':(+20,+15),'summer':'JJA','winter':'DJF'},
		'CNA':{'color':'gray','pos_off':(+8,-8),'summer':'JJA','winter':'DJF'},
		'ENA':{'color':'darkgreen','pos_off':(+23,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},
		# 'CAM':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'color':'darkgreen','pos_off':(-23,+5),'summer':'JJA','winter':'DJF'},
		'CEU':{'color':'darkblue','pos_off':(+6,+7),'summer':'JJA','winter':'DJF'},
		'CAS':{'color':'darkgreen','pos_off':(-3,+13),'summer':'JJA','winter':'DJF'},
		'NAS':{'color':'gray','pos_off':(-6,+11),'summer':'JJA','winter':'DJF'},
		'TIB':{'color':'darkcyan','pos_off':(-5,-16),'summer':'JJA','winter':'DJF'},
		'EAS':{'color':'darkgreen','pos_off':(-3,0),'summer':'JJA','winter':'DJF'},

		'MED':{'color':'gray','pos_off':(-16,-10),'summer':'JJA','winter':'DJF'},
		'WAS':{'color':'darkcyan','pos_off':(-7,-10),'summer':'JJA','winter':'DJF'},
		'mid-lat':{'edge':'darkgreen','color':'none','alpha':1,'pos':(-130,27),'summer':'JJA','winter':'DJF','scaling_factor':1.1}}







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
