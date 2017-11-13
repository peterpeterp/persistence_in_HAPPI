import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import matplotlib.pylab as plt 
import dimarray as da
from scipy.optimize import curve_fit
from lmfit import  Model
import pandas as pd


os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
try:
    import plot_map as plot_map; reload(plot_map)
except ImportError:
    raise ImportError(
        "cannot find plot_map code")
from plot_map import col_conv
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')


seasons=['MAM','JJA','SON','DJF','year']
scenarios=['Plus20-Future','Plus15-Future','All-Hist']

dataset='MIROC'
#dataset='NORESM1'

MIROC=read_nc('data/MIROC_summary.nc')['summary']
lon,lat=MIROC.lon,MIROC.lat

region_dict={}
for region in srex.keys():	
	region_dict[region]={}
	tmp={}
	for scenario in scenarios:
		region_dict[region][scenario]={}
		for season in seasons:
			region_dict[region][scenario][season]={}
			for state in ['cold','warm']:
				region_dict[region][scenario][season][state]={'mean':[],'qu_95':[]}

	polygon=Polygon(srex[region]['points'])
	for x in lon:
		if x>180:
			x__=x-360
		else:
			x__=x
		for y in lat:
			if polygon.contains(Point(x__,y)):
				for scenario in scenarios:
					for season in seasons:
						for state in ['cold','warm']:
							region_dict[region][scenario][season][state]['mean'].append(MIROC[scenario][season][state]['mean'][y][x])

def example_plot(subax):
	subax.plot([1,1],[1,1],label='projections')
	subax.plot([1,1],[1,1],label='single-exp')
	subax.plot([1,1],[1,1],label='double-exp')
	subax.set_yscale('log')
	subax.set_xlim((0,40))
	subax.set_ylim((100,1000000))
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom='on') 
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft='on') 
	subax.set_title('example')
	subax.legend(loc='best',fontsize=12)

def summary_distr_plot(subax,region):
	tmp=region_dict[region]	
	for scenario in scenarios:
		hist=np.histogram(tmp[scenario]['JJA']['warm']['mean'],256,range=[2,8],density=True)
		x=np.asarray([(hist[1][i]+hist[1][i+1])/2 for i in xrange(len(hist[1])-1)])
		y=hist[0]
		subax.plot(x,y,label=scenario)

	subax.set_xlim((2,8))
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom='off') 
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft='off') 
	subax.annotate('   '+region, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')

srex_overview.srex_overview(summary_distr_plot,srex_polygons=srex,output_name='plots/srex_mean_distr.png',example_plot=None)


def summary_plot(subax,region):
	tmp=region_dict[region]	
	for scenario in scenarios:
		subax.plot([1,1],[1,1],label=scenario+' '+str(round(np.nanmean(tmp[scenario]['JJA']['warm']['mean']),2)))

	subax.set_xlim((2,8))
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom='off') 
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft='off') 
	subax.annotate('   '+region, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
	subax.legend(loc='best',fontsize=6)


srex_overview.srex_overview(summary_plot,srex_polygons=srex,output_name='plots/srex_mean.png',example_plot=None)





