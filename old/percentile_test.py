import os,sys,glob,time,collections,gc
import numpy as np
from scipy import stats
import matplotlib.pylab as plt 
import dimarray as da
from scipy import stats

os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
import plot_map as plot_map; reload(plot_map)
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')

os.chdir('/Users/peterpfleiderer/Documents/Projects/weather_persistence')
import persistence_support as persistence_support; reload(persistence_support)
from persistence_support import *
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')


big_dict={}
for dataset in ['HadGHCND','MIROC5','NORESM1']:

	pkl_file = open('data/'+dataset+'_regional_distrs.pkl', 'rb')
	region_dict = pickle.load(pkl_file)	;	pkl_file.close()

	big_dict[dataset]=region_dict


counter=big_dict['MIROC5']['CEU']['All-Hist']['JJA']['warm']['counter']

cold,warm=counter_to_list(counter)


num_bins = 65
counts, bin_edges = np.histogram(warm, bins=range(0,65), normed=True)
cdf = np.cumsum(counts)
plt.plot(bin_edges[1:], cdf)
plt.plot([0,70],[0.95,0.95])
plt.show()

def quantile_from_cdf(x,qu):
	counts, bin_edges = np.histogram(warm, bins=range(0,max(x)+1), normed=True)
	cdf = np.cumsum(counts)

	quantiles=[]
	for q in qu:
		x1=np.where(cdf<q)[0][-1]
		quantiles.append(x1+(q-cdf[x1])/(cdf[x1+1]-cdf[x1]))

	return quantiles