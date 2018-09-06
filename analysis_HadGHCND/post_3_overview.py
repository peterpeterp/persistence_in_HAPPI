import os,sys,glob,time,collections,gc,pickle
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon, MultiPolygon
import matplotlib.pylab as plt 

os.chdir('/Users/peterpfleiderer/Documents/Scripts/allgemeine_scripte')
try:
    import plot_map as plot_map; reload(plot_map)
except ImportError:
    raise ImportError(
        "cannot find plot_map code")
from plot_map import col_conv
os.chdir('/Users/peterpfleiderer/Documents/Projects/HadGHCND_persistence')


#scenario='Nat-Hist'
scenario='HadGHCND'
#scenario='Plus20-Future'

season='JJA'

pkl_file = open('data/'+scenario+'_summary.pkl', 'rb')
distr_dict = pickle.load(pkl_file)	;	pkl_file.close()  

persis = plot_map.make_colormap([col_conv('blue'), col_conv('green'), 0.25, col_conv('green'), col_conv('yellow'), 0.5, col_conv('yellow'), col_conv('red'), 0.75, col_conv('red'), col_conv('pink')])
persis = plot_map.make_colormap([col_conv('blue'), col_conv('green'), 0.33, col_conv('green'), col_conv('yellow'), 0.66, col_conv('yellow'), col_conv('red')])

to_plot=distr_dict[season][-1]['mean'][1:-1,1:-1]
to_plot[to_plot==0]=np.nan

plot_map.plot_map(to_plot,distr_dict['lat'][1:-1],distr_dict['lon'][1:-1],color_palette=persis,color_range=[2,9],out_file='plots/mean_'+season+'.png')
