import os,sys,glob,time,collections,gc

for home_path in ['/Users/peterpfleiderer/Projects/Persistence','Dokumente/klima_uni/Persistence_small']:
	try:
		os.chdir(home_path)
	except:
		pass

os.chdir('persistence_in_HAPPI/plot_paper_final')
import __plot_imports; reload(__plot_imports); from __plot_imports import *
os.chdir('../../')

import seaborn as sns
sns.set_style("whitegrid")

from matplotlib import rc
rc('text', usetex=True)

from matplotlib import rcParams
rcParams['font.family'] = 'Arial'

cmap = {'warm': matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","yellow","darkred"]),
		'dry': matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","yellow","saddlebrown"]),
		'dry-warm': matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","pink","darkmagenta"]),
		'5mm': matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","cyan","darkcyan"])}

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

big_summary={}
big_summary['EOBS'] = da.read_nc('data/EOBS/EOBS_SummaryMeanQu.nc')['SummaryMeanQu']
big_summary['HadGHCND'] = da.read_nc('data/HadGHCND/HadGHCND_SummaryMeanQu.nc')['SummaryMeanQu']

sys.path.append("/Users/peterpfleiderer/Projects/git-packages/ScientificColourMaps5/lajolla")
from lajolla import *

models = {}
for model in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree']:
	models[model] = da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu_1x1.nc')

season='JJA'

color_range={'warm':{'mean':(3.5,6.5),'qu_95':(7,17)},
			'cold':{'mean':(3,7),'qu_95':(5,20)},
			'dry':{'mean':(3,14),'qu_95':(5,20)},
			'5mm':{'mean':(1,2),'qu_95':(2,10)},
			'dry-warm':{'mean':(1,4),'qu_95':(5,14)},
			'wet-cold':{'mean':(1,4),'qu_95':(4,10)},
			}

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rainy'}


# ------------------- other
stat,title = 'mean','Mean'
plt.close('all')
fig,axes = plt.subplots(nrows=1,ncols=4,figsize=(8,1),subplot_kw={'projection': ccrs.Robinson(central_longitude=0, globe=None)}, gridspec_kw = {'height_ratios':[10],'width_ratios':[7,7,1.4,1]})
#
# for ax in list(axes[0,:].flatten()) :
# 	ax.outline_patch.set_edgecolor('white')

for state,row in zip(['warm'],range(1)):
	im={}
	for name,letter,data,ax in zip(['HAPPI','HadGHCND','EOBS'],['a','b','c'],[models,big_summary['HadGHCND'],big_summary['EOBS']],axes[:]):
		to_plot = None
		if name == 'EOBS':
			ax.set_extent([-15,60,10,80],crs=ccrs.PlateCarree())
		else:
			ax.set_extent([-15,345,10,80],crs=ccrs.PlateCarree())

		if name == 'HAPPI':
			ensemble=np.zeros([4,180,360])*np.nan
			for model,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
				ensemble[i,:,:]=models[model]['*'.join(['All-Hist',season,state,stat])]
			to_plot=models[model]['*'.join(['All-Hist',season,state,stat])].copy()
			to_plot.values=np.roll(np.nanmean(ensemble,axis=0),180,axis=-1)
			to_plot.lon=np.roll(to_plot.lon,180,axis=-1)
		elif name=='EOBS':
			to_plot=data['All-Hist',season,state,stat]
		elif (name=='HadGHCND' and state=='warm'):
			to_plot=data['All-Hist',season,state,stat]

		if to_plot is not None:
			ax.annotate(name, xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9,fontweight='bold')
			ax.annotate(letter, xy=(0.02, 0.95), xycoords='axes fraction', fontsize=10,fontweight='bold', backgroundcolor='w')
			crange=color_range[state][stat]
			im[stat]=ax.pcolormesh(to_plot.lon,to_plot.lat,to_plot ,vmin=crange[0],vmax=crange[1],cmap=lajolla_map,transform=ccrs.PlateCarree());
			ax.coastlines(color='black')
		else:
			ax.coastlines(color='white')
			ax.outline_patch.set_edgecolor('white')

	axes[-1].outline_patch.set_edgecolor('white')
	cbar_ax=fig.add_axes([0.75,0.1,0.2,0.8])
	cbar_ax.axis('off')
	cb=fig.colorbar(im[stat],orientation='vertical',ax=cbar_ax) #95th percentile\n persistence [days]
	cb.set_label(label='Mean warm\npersistence [days]', fontsize=7)
	cb.ax.tick_params(labelsize=7)
	tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()

# plt.suptitle(title+' persistence', fontweight='bold')
fig.tight_layout()
plt.savefig('plots/final/map_validation_'+stat+'_warm.pdf')
