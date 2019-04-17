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
	ax.plot([x-0.5,x-0.5],[-2,15],color='k')
	ax.text(x,13.7,label,ha='center',va='bottom',rotation=90,fontsize=8,weight="bold")

	if c_range == 'maxabs':
		maxabs = np.max(np.abs(np.nanpercentile(var,[10,90])))
		c_range = [-maxabs,maxabs]

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

	if c_range is None:
		c_range = [np.min(var),np.max(var)]
	y= -0.7
	for x_shi,val in zip([-0.33,0,+0.33],[c_range[0],np.mean(c_range),c_range[1]]):
		polygon = Polygon([(x+x_shi-0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi+y_wi),(x+x_shi-0.33*0.5,y+y_shi+y_wi)], True)
		patches.append(polygon)
		colors.append(val)
		ax.text(x+x_shi,-1.3,round(val,02),ha='center',va='top',rotation=-90,fontsize=8,weight="bold")

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

period_count = da.read_nc('data/period_count.nc')['period_count']

summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']
state_count = da.read_nc('data/state_count_srex.nc')['state_count']
artificial = da.read_nc('data/artificial/reg_summary_mean_qu_artificial.nc')['artificial_summary']

exceed_summary = da.read_nc('/Users/peterpfleiderer/Projects/Persistence/data/JJA_summary_srex.nc')['exceed_prob']
exceed_artificial = da.read_nc('/Users/peterpfleiderer/Projects/Persistence/data/artificial/JJA_summary_srex_artificial.nc')['exceed_prob']
exceed_summary = da.concatenate((exceed_summary,exceed_artificial),align=True, axis = 'scenario')


plt.close('all')
with PdfPages('plots/table_artificial.pdf') as pdf:
	for state,state_name,style,excee,c_range in zip(['dry','5mm'],['dry','rain'],['pr','pr'],['14','7'],[(-15,15),(-30,30)]): #   }.items(): #
		fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(4,6))
		ax.axis('off')

		ax.text(0,15,"\n".join(textwrap.wrap('drivers of '+state_name+' persistence',12)),fontsize=9,va='center',weight='bold')

		for region,y_reg in regions.items():
			ax.plot([0,8.5],[y_reg-0.5,y_reg-0.5],color='k')
			ax.text(0,y_reg,region,va='center',weight='bold')
		ax.plot([0,8.5],[13.5,13.5],color='k')
		ax.text(0,-1,'scale',va='center',weight='bold')

		x=1
		# __________________________________
		x += 1
		var = (state_count[:,'JJA',state,:,'All-Hist'] ) *100
		im_state_hist = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('historic fraction of '+state_name+' days',15)), cmap='Wistia', c_range=None)
		# __________________________________

		# __________________________________
		x += 1
		var = (state_count[:,'JJA',state,:,'Plus20-Future'] - state_count[:,'JJA',state,:,'All-Hist'] ) *100
		im_state_change = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('change in fraction of '+state_name+' days',15)), cmap='RdBu_r', c_range='maxabs')

		# __________________________________
		x += 1
		var = (period_count[:,:,'Plus20-Future',state,'JJA',0] - period_count[:,:,'All-Hist',state,'JJA',0] ) / period_count[:,:,'All-Hist',state,'JJA',0] *100
		im_state_change = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('rel. change in number of '+state_name+' periods [%]',15)), cmap='RdBu_r', c_range='maxabs')


		# __________________________________

		ax.text(x+0.6,16.5,"\n".join(textwrap.wrap('rel. change in probability of exceeding '+excee+' '+state_name+' days',25)) ,fontsize=9,va='center',weight='bold')
		ax.plot([x+0.5,x+0.5],[0,18],color='k')

		# __________________________________
		x += 1
		var = (exceed_summary[:,'Plus20-Artificial-v1',:,style+'_'+state,excee] - exceed_summary[:,'All-Hist',:,style+'_'+state,excee]) / exceed_summary[:,'All-Hist',:,style+'_'+state,excee] *100
		im_pers = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('randomly added (removed) '+state+' days',10)), cmap='PiYG_r', c_range=c_range)
		# __________________________________

		# __________________________________
		x += 1
		var = (exceed_summary[:,'Plus20-Future',:,style+'_'+state,excee] - exceed_summary[:,'All-Hist',:,style+'_'+state,excee]) / exceed_summary[:,'All-Hist',:,style+'_'+state,excee] *100
		im_pers = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('projected by GCMs',10)), cmap='PiYG_r', c_range=c_range)
		# __________________________________

		ax.set_xlim(0,8)
		ax.set_ylim(-2,17.3)

		fig.tight_layout(); pdf.savefig(); plt.close()

	#################
	# model legend
	#################
	fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(3,2))
	ax.axis('off')
	xx,yy = 0,0
	patches = []
	for model in model_shifts.keys():
		x_shi,y_shi = model_shifts[model]
		polygon = Polygon([(xx+x_shi-x_wi,yy+y_shi-y_wi),(xx+x_shi+x_wi,yy+y_shi-y_wi),(xx+x_shi+x_wi,yy+y_shi+y_wi),(xx+x_shi-x_wi,yy+y_shi+y_wi)], True)
		ax.annotate(model, xy=(xx+ x_shi,yy+ y_shi), xytext=(xx+x_shi*3,yy+y_shi*3),arrowprops=dict(facecolor='k',edgecolor='m', arrowstyle="->", lw = 2),fontsize=7,color='k',ha='center',rotation=0)

		patches.append(polygon)

	colors = range(4)

	p = PatchCollection(patches, cmap='gray', alpha=1)
	p.set_array(np.array(range(4)))
	ax.add_collection(p)

	ax.set_xlim(-1,1)
	ax.set_ylim(-1,1)

	fig.tight_layout(); pdf.savefig(); plt.close()









#
