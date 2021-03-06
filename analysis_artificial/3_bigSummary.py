import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da

try:
	os.chdir('/global/homes/p/pepflei/')
except:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')

sys.path.append('weather_persistence/')
import persistence_support as persistence_support; reload(persistence_support)
from persistence_support import *

sys.path.append('persistence_in_models/')
import __settings
model_dict=__settings.model_dict

models = ['CAM4-2degree','MIROC5','NorESM1','ECHAM6-3-LR']
scenarios = ['Plus20-Artificial-v1']
styles = ['pr','pr']
states = ['dry','5mm']
styleStates = [sty+'_'+sta for sty,sta in zip(styles,states)]

out_file={
	'length' : da.DimArray(['7','14','21','28'],axes=[['7','14','21','28']],dims=['length']),
	'model' : da.DimArray(models,axes=[models],dims=['model']),
	'scenario' : da.DimArray(scenarios,axes=[scenarios],dims=['scenario']),
	'styleState' : da.DimArray(styleStates,axes=[styleStates],dims=['styleState']),
}

masks = da.read_nc('masks/srex_mask_'+model_dict['MIROC5']['grid']+'.nc')
regions = masks.keys()+['mid-lat']
out_file['exceed_prob'] = da.DimArray(axes=[models,scenarios,regions,styleStates,['7','14','21','28']],dims=['model','scenario','region','styleState','length'])

for model in models:
	print('**************'+model+'**************')

	pkl_file=open('data/artificial/'+model+'_regional_distrs_srex_artificial.pkl', 'rb')
	reg_dict = pickle.load(pkl_file);	pkl_file.close()
		# pkl_file=open('data/'+model+'/'+style+'_'+model+'_regional_distrs_mid-lat.pkl', 'rb')
		# reg_dict['NHml'] = pickle.load(pkl_file)['mid-lat'];	pkl_file.close()

	for style,state in zip(styles,states):

		for scenario in scenarios:
			for region in ['EAS','TIB','CAS','WAS','MED','CEU','NEU','NAS','ENA','CNA','WNA','CGI','ALA']:
				for per_len in [7,14,21,28]:
					tmp = reg_dict[region][scenario][state]['JJA']
					out_file['exceed_prob'][model,scenario,region,style+'_'+state,str(per_len)] = np.sum(tmp['count'][per_len:])/float(np.sum(tmp['count'])) * 100

out_file = da.Dataset(out_file)
out_file.write_nc('data/artificial/JJA_summary_srex_artificial.nc','w')
