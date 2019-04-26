import os,sys,glob,time,collections,gc,pickle,textwrap

for home_path in ['/Users/peterpfleiderer/Projects/Persistence','~/Dokumente/klima_uni/Persistence_small']:
	try:
		os.chdir(home_path)
	except:
		pass

sys.path.append('persistence_in_HAPPI/plot_paper')
from __plot_imports import *


summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']

state_dict = {
	'warm' : {'cor':''},
	'dry' : {'cor':''},
	'dry-warm' : {'cor':''},
	'5mm' : {'cor':''},
}

drive = da.DimArray( axes=[summary.region,summary.state,np.append('ensemble',summary.model),['cor','cor_signi','change','change_signi','drive','drive_signi']], dims=['region','state','model','type'])
for region in summary.region:
	for state in summary.state:
		tmp = summary['All-Hist',:,state,'EKE',region,:,'JJA']

		drive[region,state,summary.model,'cor'] = tmp[:,'corrcoef'+state_dict[state]['cor']]
		drive[region,state,'ensemble','cor'] = np.nanmean(tmp[:,'corrcoef'+state_dict[state]['cor']])

		drive[region,state,summary.model,'cor_signi'] = tmp[:,'p-value'+state_dict[state]['cor']]
		drive[region,state,ensemble,'cor'] = 

		asdas















#
