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
	KS=da.read_nc('data/'+model+'/'+model+'_SummaryKS.nc')['SummaryKS']
	ks_JJA_warm=KS['Plus20-Future','JJA','warm','KS_vs_All-Hist']
	data=da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc')
	summary=data['SummaryMeanQu']
	lon=data['lon']; lon.units="degrees_east"
	lat=data['lat']; lat.units="degrees_north"
	change_JJA_warm=summary['Plus20-Future','JJA','warm']-summary['All-Hist','JJA','warm']
	ds=da.Dataset({'mean_pers':change_JJA_warm['mean'],'95th_pers':change_JJA_warm['qu_95'],'lon':lon,'lat':lat,'KS':ks_JJA_warm})
	ds.write_nc('data/'+model+'/'+model+'_diff_JJA-warm.nc', mode='w')
	os.system('cdo remapbil,data/grid1x1.cdo data/'+model+'/'+model+'_diff_JJA-warm.nc data/'+model+'/'+model+'_diff_JJA-warm_1x1.nc')


for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	os.system('cdo remapbil,data/grid1x1.cdo data/EKE/EKE_diff_2vshist_'+model+'_monClim.nc data/EKE/EKE_diff_2vshist_'+model+'_monClim_1x1.nc')


for style in ['tas','pr','cpd']:
	for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
		data=da.read_nc('data/'+model+'/'+style+'_'+model+'_SummaryMeanQu.nc')
		lon=data['lon']; lon.units="degrees_east"
		lat=data['lat']; lat.units="degrees_north"
		ds={'lon':lon,'lat':lat}
		tmp=data['SummaryMeanQu']
		for scenario in tmp.scenario:
			for season in tmp.season:
				for state in tmp.state:
					for stat_type in ['mean','qu_95']:
						ds['*'.join([scenario,season,state,stat_type])]=tmp[scenario,season,state,stat_type]
		da.Dataset(ds).write_nc('data/'+model+'/'+style+'_'+model+'_SummaryMeanQu_regridReady.nc', mode='w')
		os.system('cdo remapbil,data/grid1x1.cdo data/'+model+'/'+style+'_'+model+'_SummaryMeanQu_regridReady.nc data/'+model+'/'+style+'_'+model+'_SummaryMeanQu_1x1.nc')

for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	for filename in glob.glob('data/'+model+'/state_stats/*'):
		os.system('cdo remapbil,data/grid1x1.cdo '+filename + ' ' + filename.replace('.nc','_1x1.nc'))
