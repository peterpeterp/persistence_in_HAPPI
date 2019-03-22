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
sns.set()
sns.set_style("whitegrid")
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')

working_path='/p/tmp/pepflei/HAPPI/raw_data/reg_cor/'

model_shifts = {
	'CAM4-2degree':(-0.25,-0.25),
	'ECHAM6-3-LR':(+0.25,-0.25),
	'MIROC5':(+0.25,+0.25),
	'NorESM1':(-0.25,+0.25),
}

x_wi = 0.25
y_wi = 0.25

state_dict = {
	'warm':'tas',
	# 'dry':'pr',
	'5mm':'pr',
	# '10mm':'pr',
	'dry-warm':'cpd',
	}

regions = {'EAS':1,
			'TIB':2,
			'CAS':3,
			'WAS':4,
			'MED':5,
			'CEU':6,
			'ENA':7,
			'CNA':8,
			'WNA':9,
			'NAS':10,
			'NEU':11,
			'CGI':12,
			'ALA':13,
}


for model in ['CAM4-2degree','MIROC5','ECHAM6-3-LR','NorESM1']:
	tmp_1 = {}
	for state,style in state_dict.items():
		tmp_2 = {}
		for corWith_name in ['EKE','SPI3']:

			hist = da.read_nc(working_path+model+'/cor_'+corWith_name+'_'+'_'.join([model,'All-Hist','*',state])+'.nc', align=True, axis='region')
			hist.region = [dd.split('_')[-2] for dd in hist.region]
			hist = da.stack(hist, axis='statistic', align=True )

			fut = da.read_nc(working_path+model+'/cor_'+corWith_name+'_'+'_'.join([model,'Plus20-Future','*',state])+'.nc', align=True, axis='region')
			fut.region = [dd.split('_')[-2] for dd in fut.region]
			fut = da.stack(fut, axis='statistic', align=True )

			tmp_2[corWith_name] = da.stack((hist,fut), axis='scenario', keys=['All-Hist','Plus20-Future'])

		tmp_1[state] = da.stack(tmp_2, axis='corWith', align=True)

	# data = da.stack(tmp_1, axis='state', align=True)
	da.Dataset(tmp_1).write_nc(working_path+'/cor_Summary_'+model+'.nc')

	tmp = da.stack(tmp_1, axis='state', align=True)
	summary = {}
	summary['mean'] = tmp.ix[:,:,:,:,:,:,0,0].copy() *np.nan
	summary['mean'].values = np.nanmean(tmp,axis=(-2,-1))




	asdas





#
