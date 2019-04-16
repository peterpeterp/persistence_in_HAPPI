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
	'dry':'pr',
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
	print(model)
	tmp_1 = {}
	for state,style in state_dict.items():
		print(state)
		tmp_2 = {}
		for corWith_name in ['EKE','SPI3']:
			print(corWith_name)

			hist_files = glob.glob(working_path+model+'/cor_'+corWith_name+'_'+'_'.join([model,'All-Hist','*',state])+'.nc')
			hist = {}
			for hist_file in hist_files:
				region = hist_file.split('_')[-2]
				hist[region] = da.stack(da.read_nc(hist_file),axis='statistic',align=True)
				hist[region].lat = np.round(hist[region].lat,02)
				hist[region].lon = np.round(hist[region].lon,02)
			hist = da.stack(hist, align=True, axis='region')

			fut_files = glob.glob(working_path+model+'/cor_'+corWith_name+'_'+'_'.join([model,'Plus20-Future','*',state])+'.nc')
			fut = {}
			for fut_file in fut_files:
				region = fut_file.split('_')[-2]
				fut[region] = da.stack(da.read_nc(fut_file),axis='statistic',align=True)
				fut[region].lat = np.round(fut[region].lat,02)
				fut[region].lon = np.round(fut[region].lon,02)
			fut = da.stack(fut, align=True, axis='region')

			tmp_2[corWith_name] = da.stack((hist,fut), axis='scenario', keys=['All-Hist','Plus20-Future'], align=True)


		tmp_1[state] = da.stack(tmp_2, axis='corWith', align=True)

	# data = da.stack(tmp_1, axis='state', align=True)
	da.Dataset(tmp_1).write_nc(working_path+'/cor_Summary_'+model+'_gridded.nc')

working_path='/p/tmp/pepflei/HAPPI/raw_data/reg_stats/'

for model in ['NorESM1','CAM4-2degree','MIROC5','ECHAM6-3-LR']:
	tmp_1 = {}
	for state,style in state_dict.items():
		tmp_2 = {}
		for corWith_name in ['EKE','SPI3']:

			hist_files = glob.glob(working_path+model+'/stats_'+corWith_name+'_'+'_'.join([model,'All-Hist','*',state])+'.nc')
			hist = {}
			for hist_file in hist_files:
				region = hist_file.split('_')[-2]
				hist[region] = da.stack(da.read_nc(hist_file),axis='statistic',align=True)
				hist[region].lat = np.round(hist[region].lat,02)
				hist[region].lon = np.round(hist[region].lon,02)
			hist = da.stack(hist, align=True, axis='region')

			fut_files = glob.glob(working_path+model+'/stats_'+corWith_name+'_'+'_'.join([model,'Plus20-Future','*',state])+'.nc')
			fut = {}
			for fut_file in fut_files:
				region = fut_file.split('_')[-2]
				fut[region] = da.stack(da.read_nc(fut_file),axis='statistic',align=True)
				fut[region].lat = np.round(fut[region].lat,02)
				fut[region].lon = np.round(fut[region].lon,02)
			fut = da.stack(fut, align=True, axis='region')

			tmp_2[corWith_name] = da.stack((hist,fut), axis='scenario', keys=['All-Hist','Plus20-Future'], align=True)


		tmp_1[state] = da.stack(tmp_2, axis='corWith', align=True)

	# data = da.stack(tmp_1, axis='state', align=True)
	da.Dataset(tmp_1).write_nc(working_path+'/stats_Summary_'+model+'_gridded.nc')
