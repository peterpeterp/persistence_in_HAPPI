import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')


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
