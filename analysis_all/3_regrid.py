import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	data=da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc')
	lon=data['lon']; lon.units="degrees_east"
	lat=data['lat']; lat.units="degrees_north"
	ds={'lon':lon,'lat':lat}
	tmp=data['SummaryMeanQu']
	for scenario in tmp.scenario:
		for season in tmp.season:
			for state in tmp.state:
				for stat_type in ['mean','qu_95']:
					ds['*'.join([scenario,season,state,stat_type])]=tmp[scenario,season,state,stat_type]
	da.Dataset(ds).write_nc('data/'+model+'/'+model+'_SummaryMeanQu_regridReady.nc', mode='w')
	os.system('cdo remapbil,data/grid1x1.cdo data/'+model+'/'+model+'_SummaryMeanQu_regridReady.nc data/'+model+'/'+model+'_SummaryMeanQu_1x1.nc')

for model in ['ECHAM6-3-LR','MIROC5','NorESM1','CAM4-2degree']:
	data=da.read_nc('data/'+model+'/'+model+'_EsceedanceProb_gridded.nc')
	lon=data['lon']; lon.units="degrees_east"
	lat=data['lat']; lat.units="degrees_north"
	ds={'lon':lon,'lat':lat}
	tmp=data['ExceedanceProb']
	for scenario in tmp.scenario:
		for season in tmp.season:
			for state in tmp.state:
				for thresh in [3,4,5,6,7,10,14,21,28]:
					ds['*'.join([scenario,season,state,str(thresh)])]=tmp[scenario,season,state,thresh]
	da.Dataset(ds).write_nc('data/'+model+'/'+model+'_EsceedanceProb_gridded_regridReady.nc', mode='w')
	os.system('cdo remapbil,data/grid1x1.cdo data/'+model+'/'+model+'_EsceedanceProb_gridded_regridReady.nc data/'+model+'/'+model+'_EsceedanceProb_gridded_1x1.nc')


for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	data=da.read_nc('data/'+model+'/'+model+'_EsceedanceProb_gridded.nc')
	lon=data['lon']; lon.units="degrees_east"
	lat=data['lat']; lat.units="degrees_north"
	ds={'lon':lon,'lat':lat}

	state_dict = {
		'warm':'tas',
		'dry':'pr',
		'5mm':'pr',
		'dry-warm':'cpd',
		}

	for state in ['warm','dry','dry-warm','5mm']:
		for scenario in ['All-Hist','Plus20-Future','Plus15-Future']:
			tmp = da.read_nc('data/'+model+'/state_stats/'+state_dict[state]+'_'+model+'_'+scenario+'_stateCount.nc')
			ds['*'.join([scenario,'JJA',state])] = tmp[state]['JJA'] / np.array(tmp[state+'_possible_days']['JJA'],np.float)

	da.Dataset(ds).write_nc('data/'+model+'/state_stats/'+model+'_stateCount_regridReady.nc', mode='w')
	os.system('cdo -O remapbil,data/grid1x1.cdo data/'+model+'/state_stats/'+model+'_stateCount_regridReady.nc data/'+model+'/state_stats/'+model+'_stateCount_1x1.nc')



# for model in ['ECHAM6-3-LR','MIROC5','NorESM1','CAM4-2degree']:
# 	data=da.read_nc('data/'+model+'/'+model+'_StateCount.nc')
# 	lon=data['lon']; lon.units="degrees_east"
# 	lat=data['lat']; lat.units="degrees_north"
# 	ds={'lon':lon,'lat':lat}
# 	tmp=data['SummaryMeanQu']
# 	for scenario in tmp.scenario:
# 		for season in tmp.season:
# 			for state in tmp.state:
# 				ds['*'.join([scenario,season,state])]=tmp[scenario,season,state]
# 	da.Dataset(ds).write_nc('data/'+model+'/'+model+'_StateCount_regridReady.nc', mode='w')
# 	os.system('cdo remapbil,data/grid1x1.cdo data/'+model+'/'+model+'_StateCount_regridReady.nc data/'+model+'/'+model+'_StateCount_1x1.nc')
#




# for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
# 	KS=da.read_nc('data/'+model+'/'+model+'_SummaryKS.nc')['SummaryKS']
# 	ks_JJA_warm=KS['Plus20-Future','JJA','warm','KS_vs_All-Hist']
# 	data=da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc')
# 	summary=data['SummaryMeanQu']
# 	lon=data['lon']; lon.units="degrees_east"
# 	lat=data['lat']; lat.units="degrees_north"
# 	change_JJA_warm=summary['Plus20-Future','JJA','warm']-summary['All-Hist','JJA','warm']
# 	ds=da.Dataset({'mean_pers':change_JJA_warm['mean'],'95th_pers':change_JJA_warm['qu_95'],'lon':lon,'lat':lat,'KS':ks_JJA_warm})
# 	ds.write_nc('data/'+model+'/'+model+'_diff_JJA-warm.nc', mode='w')
# 	os.system('cdo remapbil,data/grid1x1.cdo data/'+model+'/'+model+'_diff_JJA-warm.nc data/'+model+'/'+model+'_diff_JJA-warm_1x1.nc')
#

# for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
# 	os.system('cdo remapbil,data/grid1x1.cdo data/EKE/EKE_diff_2vshist_'+model+'_monClim.nc data/EKE/EKE_diff_2vshist_'+model+'_monClim_1x1.nc')




##
