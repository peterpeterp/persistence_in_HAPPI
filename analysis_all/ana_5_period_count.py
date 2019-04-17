import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da
from scipy.optimize import curve_fit
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy import stats

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker

import seaborn as sns
sns.set_style("whitegrid")


sys.path.append('/Users/peterpfleiderer/Projects/allgemeine_scripte')
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

big_dict={}
for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
	pkl_file=open(infile, 'rb')
	big_dict[dataset] = pickle.load(pkl_file);	pkl_file.close()

periods = da.DimArray( axes=[['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],big_dict[dataset].keys(),['All-Hist','Plus20-Future','Plus15-Future'],big_dict[dataset]['CEU']['All-Hist'].keys(),big_dict[dataset]['CEU']['All-Hist']['warm'].keys(),range(40)], dims=['model','region','scenario','state','season','period_length'])

for model in periods.model:
	for region in periods.region:
		for scenario in periods.scenario:
			for state in periods.state:
				for season in periods.season:
					tmp=big_dict[model][region][scenario][state][season]
					periods[model,region,scenario,state,season]=np.array([np.sum(tmp['count'][ii:]) for ii in range(40)])
					print(state,periods[model,region,scenario,state,season])

da.Dataset({'period_count':periods}).write_nc('data/period_count.nc')











#
