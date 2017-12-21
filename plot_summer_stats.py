import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import matplotlib.pylab as plt
import dimarray as da
from scipy.optimize import curve_fit
from lmfit import  Model
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy import stats

os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
import plot_map as plot_map; reload(plot_map)
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()




#region_dict=get_regional_distribution('HadGHCND',scenarios=['All-Hist'])

big_dict={}
for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	big_dict[dataset]=da.read_nc('data/'+dataset+'_SummarySummer.nc')['summerStats']






# ---------------------------- distr comparison
def legend_plot(subax):
	subax.axis('off')
	for dataset,color in zip(['HadGHCND','MIROC5','NorESM1','CAM4','CanAM4'],['black','blue','green','magenta','orange']):
		subax.plot([1,1],[1,1],label=dataset,c=color)
	subax.legend(loc='best',fontsize=12)

def example_plot(subax):
	subax.set_yscale('log')
	subax.set_xlim((0,40))
	subax.set_ylim((0.0001,0.5))
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom='on')
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft='on')
	subax.set_ylabel('PDF')
	subax.set_xlabel('days')
	subax.set_title('example')
	subax.locator_params(axis = 'x', nbins = 5)

def annotate_plot(subax,arg1=None,arg2=None,arg3=None):
	subax.axis('off')
	subax.text(0.5,0.5,arg1+' '+arg2,fontsize=14)

def distrs(subax,region,arg1=None,arg2=None,arg3=None):
	for dataset,color in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],['blue','green','magenta','orange']):
		subax.plot([0,1,2],big_dict[dataset][['All-Hist','Plus15-Future','Plus20-Future'],region,'mean_hot_temp'],color=color)

	# subax.set_yscale('log')
	# subax.set_xlim((0,40))
	# subax.set_ylim((0.0001,0.5))
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom='off')
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft='off')
	subax.locator_params(axis = 'x', nbins = 5)

	subax.annotate('   '+region, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')

ax=srex_overview.srex_overview_NH(distrs,srex_polygons=srex,output_name='plots/summer_stats_NH.png')

# fig = plt.figure(figsize=(10,2.5))
# ax_example=fig.add_axes([0.1,0.3,0.15,0.5])
# example_plot(ax_example)
# ax_legend=fig.add_axes([0.3,0.4,0.2,0.5])
# legend_plot(ax_legend)
# plt.savefig('plots/summer_stats_NH_legend.png')
# plt.clf()
