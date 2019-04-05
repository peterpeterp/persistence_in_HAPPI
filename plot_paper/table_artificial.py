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

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

bool_styles = {-1:{'c':'green','m':'v'},
				1:{'c':'magenta','m':'^'}}
				#

def counter_to_list(counter):
	tmp=[]
	lengths=counter.keys()
	if 0 in lengths:
		lengths.remove(0)
	if len(lengths)>2:
		for key in lengths:
			for i in range(counter[key]):
				tmp.append(key)
		tmp=np.array(tmp)
		return -tmp[tmp<0],tmp[tmp>0]
	else:
		return [],[]


def plot_model_column(ax,x,var,signi=None,label=' ',c_range=(-0.5,0.5), plot_bool=False, cmap='RdBu'):
	patches = []
	colors = []
	ax.plot([x-0.5,x-0.5],[0,15],color='k')
	ax.text(x,13.7,"\n".join(textwrap.wrap(label,15)),ha='center',va='bottom',rotation=90,fontsize=8,weight="bold")
	for region,y in regions.items():
		for model in model_shifts.keys():
			x_shi,y_shi = model_shifts[model]

			if np.isfinite(var[model,region]):
				if plot_bool == False:
					polygon = Polygon([(x+x_shi-x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi-y_wi),(x+x_shi+x_wi,y+y_shi+y_wi),(x+x_shi-x_wi,y+y_shi+y_wi)], True)
					patches.append(polygon)
					colors.append(var[model,region])

				else:
					style = bool_styles[np.sign(var[model,region])]
					ax.plot(x+x_shi,y+y_shi, marker=style['m'], color=style['c'])


	p = PatchCollection(patches, cmap=cmap, alpha=1)
	p.set_array(np.array(colors))
	p.set_clim(c_range)
	im = ax.add_collection(p)

	return im

model_shifts = {
	'CAM4-2degree':(-0.25,-0.25),
	'ECHAM6-3-LR':(+0.25,-0.25),
	'MIROC5':(+0.25,+0.25),
	'NorESM1':(-0.25,+0.25),
}

x_wi = 0.25
y_wi = 0.25

regions = {'EAS':1,
			'TIB':2,
			'CAS':3,
			'WAS':4,
			'MED':5,
			'CEU':6,
			'NEU':7,
			'NAS':8,
			'ENA':9,
			'CNA':10,
			'WNA':11,
			'CGI':12,
			'ALA':13,
}

summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']
state_count = da.read_nc('data/state_count_srex.nc')['state_count']

if 'artificial' not in globals():
	artificial = da.DimArray(axes = [['Plus20-Artificial-v1'],['MIROC5','CAM4-2degree','ECHAM6-3-LR','NorESM1'], ['dry','5mm'], summary.region, summary.season, ['mean']], dims = ['scenario','model','state','region','season','statistic'])

	for scenario in artificial.scenario:
		for model in artificial.model:
			tmp = pickle.load(open('data/artificial/'+model+'_regional_distrs_srex_artificial.pkl', 'rb'))

			for state in artificial.state:
				for region in artificial.region:
					for season in artificial.season:
						neg,pos=counter_to_list(tmp[region][scenario][state][season]['counter'])
						artificial[scenario,model,state,region,season,'mean'] = np.nanmean(pos)

for state,state_name in {'dry':'dry','5mm':'rain'}.items(): #   }.items(): #

	plt.close('all')
	fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(8,6))
	ax.axis('off')

	ax.text(0,15,"\n".join(textwrap.wrap('drivers of '+state_name+' persistence',12)),fontsize=9,va='center',weight='bold')

	for region,y_reg in regions.items():
		ax.plot([0,8.5],[y_reg-0.5,y_reg-0.5],color='k')
		ax.text(0,y_reg,region,va='center',weight='bold')
	ax.plot([0,8.5],[13.5,13.5],color='k')
	x=1

	# __________________________________
	x += 1
	var = (state_count[:,'JJA',state,:,'All-Hist'] ) *100
	im_pers = plot_model_column(ax,x,var,label = 'state historic '+state_name+' ', cmap='PiYG_r', c_range=(0,100))
	# __________________________________


	# __________________________________
	x += 1
	var = (state_count[:,'JJA',state,:,'Plus20-Future'] - state_count[:,'JJA',state,:,'All-Hist'] ) *100
	im_pers = plot_model_column(ax,x,var,label = 'state '+state_name+' ', cmap='PiYG_r', c_range=(-2,2))
	# __________________________________

	# __________________________________
	x += 1
	var = artificial['Plus20-Artificial-v1',:,state,:,'JJA','mean'] - summary['All-Hist',:,state,'EKE',:,'mean_'+state,'JJA']
	im_pers = plot_model_column(ax,x,var,label = 'artificial change in mean '+state_name+' persistence', cmap='PiYG_r')
	# __________________________________

	# __________________________________
	x += 1
	var = (summary['Plus20-Future',:,state,'EKE',:,'mean_'+state,'JJA'] - summary['All-Hist',:,state,'EKE',:,'mean_'+state,'JJA'] )
	im_pers = plot_model_column(ax,x,var,label = 'change in mean '+state_name+' persistence', cmap='PiYG_r')
	# __________________________________


	#################
	# colormaps
	#################

	cbar_ax=fig.add_axes([0.75,0.5,0.2,0.3]); cbar_ax.axis('off');
	cb=fig.colorbar(im_pers,orientation='horizontal',ax=cbar_ax) #95th percentile\n persistence [days]
	cb.set_label(label='stuff with persistence', fontsize=10); cb.ax.tick_params(labelsize=10)
	tick_locator = mpl.ticker.MaxNLocator(nbins=4); cb.locator = tick_locator; cb.update_ticks()



	#################
	# model legend
	#################

	patches = []
	for model in model_shifts.keys():
		x_shi,y_shi = model_shifts[model]
		polygon = Polygon([(10.5+x_shi-x_wi,15+y_shi-y_wi),(10.5+x_shi+x_wi,15+y_shi-y_wi),(10.5+x_shi+x_wi,15+y_shi+y_wi),(10.5+x_shi-x_wi,15+y_shi+y_wi)], True)
		ax.annotate(model, xy=(10.5+ x_shi,15+ y_shi), xytext=(10.5+x_shi*3,15+y_shi*3),arrowprops=dict(facecolor='k',edgecolor='m', arrowstyle="->"),fontsize=7,color='k',ha='center',rotation=0)

		patches.append(polygon)

	patches.append(plt.Circle((10.5, 15), 0.25))
	if state == 'warm':
		ax.annotate('HadGHCND', xy=(10.5,15), xytext=(10.5+x_shi*3,15),arrowprops=dict(facecolor='k',edgecolor='m', arrowstyle="->"),fontsize=7,color='k',ha='center',rotation=0)
	else:
		ax.annotate('EOBS', xy=(10.5,15), xytext=(10.5+x_shi*3,15),arrowprops=dict(facecolor='k',edgecolor='m', arrowstyle="->"),fontsize=7,color='k',ha='center',rotation=0)

	colors = range(5)

	p = PatchCollection(patches, cmap='gray', alpha=1)
	p.set_array(np.array(range(4)))
	ax.add_collection(p)

	ax.set_xlim(0,12)
	ax.set_ylim(0,17)


	fig.tight_layout()
	plt.savefig('plots/table_artificial_'+state+'.pdf')
