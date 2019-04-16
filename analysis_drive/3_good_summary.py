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

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence')
except:
	os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')

working_path='/p/tmp/pepflei/HAPPI/raw_data/reg_cor/'

state_dict = {
	'warm':'tas',
	'dry':'pr',
	'5mm':'pr',
	'dry-warm':'cpd',
	}
#
# #################
# # gridded summary
# #################
# for model in ['CAM4-2degree','MIROC5','ECHAM6-3-LR','NorESM1']:
# 	print(model)
# 	tmp_1 = {}
# 	for state,style in state_dict.items():
# 		print(state)
# 		tmp_2 = {}
# 		for corWith_name in ['EKE','SPI3']:
# 			all_files = glob.glob('data/reg_cor/'+model+'/cor_'+corWith_name+'*All-Hist*_'+state+'.nc')
#
# 			tmp = {}
# 			for file_name in all_files:
# 				region = file_name.split('_')[-2]
# 				if region != 'NHml':
# 					tmp[region] = da.stack(da.read_nc(file_name),axis='statistic',align=True)
# 			tmp = da.stack(tmp, align=True, axis='region')
#
# 			merged = tmp['CEU'].copy() * np.nan
# 			merged.values = np.nanmean(tmp,axis=0)
#
# 			tmp_2[corWith_name] = merged
#
# 		tmp_1[state] = da.stack(tmp_2, axis='corWith', align=True)
#
# 	result = da.stack(tmp_1, axis='state', align=True)
# 	da.Dataset({'cor':result}).write_nc('data/reg_cor/Cor_summary_'+model+'.nc')

#################
# reg average summary
#################

result = {}
for scenario in ['All-Hist','Plus20-Future']:
	tmp_0 = {}
	for model in ['CAM4-2degree','MIROC5','ECHAM6-3-LR','NorESM1']:
		print(model)
		tmp_1 = {}
		for state,style in state_dict.items():
			print(state)
			tmp_2 = {}
			for corWith_name in ['EKE','SPI3']:

				all_files = glob.glob('data/reg_cor/'+model+'/cor_'+corWith_name+'*'+scenario+'*_'+state+'.nc')
				tmp_3 = {}
				for file_name in all_files:
					region = file_name.split('_')[-2]
					if region != 'NHml':
						tmp = da.stack(da.read_nc(file_name),axis='statistic',align=True)
						tmp_3[region] = tmp.mean(axis=(-2,-1))
						tmp_3[region].values = np.nanmean(tmp,axis=(-2,-1))

				all_files = glob.glob('data/reg_stats/'+model+'/stats_'+corWith_name+'*'+scenario+'*_'+state+'.nc')
				tmp_4 = {}
				for file_name in all_files:
					region = file_name.split('_')[-2]
					if region != 'NHml':
						tmp = da.stack(da.read_nc(file_name),axis='statistic',align=True)
						tmp_4[region] = tmp.mean(axis=(-2,-1))
						tmp_4[region].values = np.nanmean(tmp,axis=(-2,-1))

				tmp_3_ = da.stack(tmp_3, align=True, axis='region')
				tmp_4_ = da.stack(tmp_4, align=True, axis='region')

				tmp_2[corWith_name] = da.concatenate((tmp_3_,tmp_4_), align=True, axis='statistic')

			tmp_1[state] = da.stack(tmp_2, axis='corWith', align=True)

		tmp_0[model] = da.stack(tmp_1, axis='state', align=True)

	result[scenario] = da.stack(tmp_0, axis='model', align=True)

da.Dataset({'summary_cor':da.stack(result, axis='sceanrio', align=True)}).write_nc('data/cor_reg_summary.nc')














#
