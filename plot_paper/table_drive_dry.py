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

def plot_model_column(ax,x,var,signi=None,label=' ',c_range=(-0.3,0.3), plot_bool=False, cmap='RdBu'):
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
	for x_shi,val in zip([-0.33,0,+0.33],[c_range[0]*0.33,np.mean(c_range),c_range[1]*0.33]):
		polygon = Polygon([(x+x_shi-0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi+y_wi),(x+x_shi-0.33*0.5,y+y_shi+y_wi)], True)
		patches.append(polygon)
		colors.append(val)
		ax.text(x+x_shi,-1.3,round(val,02),ha='center',va='top',rotation=-90,fontsize=8,weight="bold")

	p = PatchCollection(patches, cmap=cmap, alpha=1)
	p.set_array(np.array(colors))
	p.set_clim(c_range)
	im = ax.add_collection(p)

	return im

def plot_obs_column(ax,x,var,masks,c_range=(-0.3,0.3), label=' ', x_shi=0 ,y_shi=0, cmap='RdBu'):
	patches = []
	colors = []
	for region,y in regions.items():
		if region in masks.keys():
			mask = masks[region].copy()
			if mask.shape != var['corrcoef']['JJA'].shape:
				mask = mask.T
			cor = np.array(var['corrcoef']['JJA'].values * mask.values).flatten()
			relevant_cells = np.where((mask.flatten()>0) & (np.isfinite(cor)))[0]
			cor = cor[relevant_cells]

			patches.append(plt.Circle((x, y), 0.25))
			colors.append(np.nansum(cor))

			homogenety = np.sum( np.sign(cor) == np.sign(np.nansum(cor)) ) / float(cor.shape[0])
			if homogenety >= 0.9:
				ax.plot([x],[y],'*k')

			mask[mask>0] = 1
			pval = np.array(var['p_value']['JJA'].values * mask.values).flatten()
			signi = np.sum( (np.sign(cor) == np.sign(np.nansum(cor))) & (pval[relevant_cells] < 0.05) ) / float(cor.shape[0])
			if signi >= 0.5:
				ax.plot([x],[y],'vk')


	p = PatchCollection(patches, cmap=cmap, edgecolor='k', alpha=1)
	p.set_array(np.array(colors))
	p.set_clim(c_range)
	ax.add_collection(p)

	return ax

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

state_dict = {
	'warm':{'style':'tas','name':'warm','excee':'14'},
	'dry':{'style':'pr','name':'dry','excee':'14'},
	'5mm':{'style':'pr','name':'rain','excee':'7'},
	'dry-warm':{'style':'cpd','name':'dry-warm','excee':'14'},
	}

summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']
had_mask = da.read_nc('masks/srex_mask_73x97.nc')
eobs_mask = da.read_nc('masks/srex_mask_EOBS.nc')
exceed_summary = da.read_nc('/Users/peterpfleiderer/Projects/Persistence/data/JJA_summary_srex.nc')['exceed_prob']

state = 'dry'
details = state_dict[state]

plt.close('all')
with PdfPages('plots/table_driver_'+state+'.pdf') as pdf:

	fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(6,6))
	ax.axis('off')

	ax.text(0,15,"\n".join(textwrap.wrap('drivers of '+details['name']+' persistence',12)),fontsize=9,va='center',weight='bold')

	for region,y_reg in regions.items():
		ax.plot([0,8.5],[y_reg-0.5,y_reg-0.5],color='k')
		ax.text(0,y_reg,region,va='center',weight='bold')
	ax.plot([0,8.5],[13.5,13.5],color='k')
	ax.text(0,-1,'scale',va='center',weight='bold')

	x=1

	x += 1
	im_eke = plot_model_column(ax,x,summary['All-Hist',:,state,'EKE',:,'corrcoef','JJA'], label='correlation\nEKE - '+details['name'], cmap='PuOr')
	if state == 'warm':
		ax = plot_obs_column(ax, x=x, var=da.read_nc('data/HadGHCND/All-Hist/cor_EKE_HadGHCND_All-Hist_'+state+'.nc'), label=' ', masks=had_mask, cmap='PuOr')
	else:
		ax = plot_obs_column(ax, x=x, var=da.read_nc('data/EOBS/All-Hist/cor_EKE_EOBS_All-Hist_'+state+'.nc'), label=' ', masks=eobs_mask, cmap='PuOr')


	x += 1
	var = summary['Plus20-Future',:,state,'EKE',:,'mean_'+'EKE','JJA'] - summary['All-Hist',:,state,'EKE',:,'mean_'+'EKE','JJA']
	im_eke = plot_model_column(ax,x,var,label = 'change in EKE', cmap='PuOr',c_range='maxabs')

	x += 1
	diff_cor = summary['Plus20-Future',:,state,'EKE',:,'mean_'+'EKE','JJA']  - summary['All-Hist',:,state,'EKE',:,'mean_'+'EKE','JJA']
	var = diff_cor / summary['All-Hist',:,state,'EKE',:,'lr_slope','JJA']
	plot_model_column(ax,x,var, label='EKE forcing on\n'+state+' persistence', plot_bool=True)

	# __________________________________
	x += 1
	var = (exceed_summary[:,'Plus20-Future',:,details['style']+'_'+state,details['excee']] - exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']]) / exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']] *100
	im_pers = plot_model_column(ax,x,var,label = 'rel. change in\nprobability of exceeding\n14 '+details['name']+' days', cmap='PiYG_r', c_range='maxabs')
	# __________________________________

	x += 1
	diff_cor = summary['Plus20-Future',:,state,'SPI3',:,'mean_'+'SPI3','JJA']  - summary['All-Hist',:,state,'SPI3',:,'mean_'+'SPI3','JJA']
	var = diff_cor / summary['All-Hist',:,state,'SPI3',:,'lr_slope','JJA']
	plot_model_column(ax,x,var, label='SPI3 forcing on \n'+state+' persistence', plot_bool=True)

	x += 1
	var = summary['Plus20-Future',:,state,'SPI3',:,'mean_'+'SPI3','JJA'] - summary['All-Hist',:,state,'SPI3',:,'mean_'+'SPI3','JJA']
	plot_model_column(ax,x,var,label = 'change in SPI3', cmap='BrBG',c_range='maxabs')

	x += 1
	im_spi = plot_model_column(ax,x,summary['All-Hist',:,state,'SPI3',:,u'corrcoef_lagged','JJA'], label='correaltion \nSPI3 - '+details['name'], cmap='BrBG')
	if state == 'warm':
		ax = plot_obs_column(ax, x=x, var=da.read_nc('data/HadGHCND/All-Hist/cor_SPI3_HadGHCND_All-Hist_'+state+'.nc'), label=' ', masks=had_mask, cmap='BrBG')
	else:
		ax = plot_obs_column(ax, x=x, var=da.read_nc('data/EOBS/All-Hist/cor_SPI3_EOBS_All-Hist_'+state+'.nc'), label=' ', masks=eobs_mask, cmap='BrBG')


	ax.set_xlim(0,9)
	ax.set_ylim(-2,17)

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
		ax.annotate(model, xy=(xx+ x_shi,yy+ y_shi), xytext=(xx+x_shi*3,yy+y_shi*3),arrowprops=dict(facecolor='k',edgecolor='m', arrowstyle="->", lw = 2),fontsize=10,color='k',ha='center',rotation=0)

		patches.append(polygon)

	patches.append(plt.Circle((xx, yy), 0.25))
	if state == 'warm':
		ax.annotate('HadGHCND', xy=(xx,yy), xytext=(xx+x_shi*3,yy),arrowprops=dict(facecolor='k',edgecolor='m', arrowstyle="->",lw = 2),fontsize=7,color='k',ha='center',rotation=0)
	else:
		ax.annotate('EOBS', xy=(xx,yy), xytext=(xx+x_shi*3,yy),arrowprops=dict(facecolor='k',edgecolor='m', arrowstyle="->",lw = 2),fontsize=7,color='k',ha='center',rotation=0)

	colors = range(5)

	p = PatchCollection(patches, cmap='gray', alpha=1)
	p.set_array(np.array(range(4)))
	ax.add_collection(p)

	ax.set_xlim(-1,1)
	ax.set_ylim(-1,1)

	fig.tight_layout(); pdf.savefig(); plt.close()
