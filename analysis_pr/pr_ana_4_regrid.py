import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import dimarray as da

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')


for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	KS=da.read_nc('data/'+model+'/pr_'+model+'_SummaryKS.nc')['SummaryKS']
	ks_JJA_dry=KS['Plus20-Future','JJA','dry','KS_vs_All-Hist']
	data=da.read_nc('data/'+model+'/pr_'+model+'_SummaryMeanQu.nc')
	summary=data['SummaryMeanQu']
	lon=data['lon']; lon.units="degrees_east"
	lat=data['lat']; lat.units="degrees_north"
	change_JJA_dry=summary['Plus20-Future','JJA','dry']-summary['All-Hist','JJA','dry']
	ds=da.Dataset({'mean_pers':change_JJA_dry['mean'],'95th_pers':change_JJA_dry['qu_95'],'lon':lon,'lat':lat,'KS':ks_JJA_dry})
	ds.write_nc('data/'+model+'/pr_'+model+'_diff_JJA-dry.nc', mode='w')
	os.system('cdo remapbil,data/grid1x1.cdo data/'+model+'/pr_'+model+'_diff_JJA-dry.nc data/'+model+'/pr_'+model+'_diff_JJA-dry_1x1.nc')


for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	os.system('cdo remapbil,data/grid1x1.cdo data/EKE/EKE_diff_2vshist_'+model+'_monClim.nc data/EKE/EKE_diff_2vshist_'+model+'_monClim_1x1.nc')
