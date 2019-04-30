import os,sys,glob,time,collections,gc,pickle,textwrap

for home_path in ['/Users/peterpfleiderer/Projects/Persistence','Dokumente/klima_uni/Persistence_small']:
	try:
		os.chdir(home_path)
	except:
		pass

os.chdir('persistence_in_HAPPI/plot_paper')
from __plot_imports import *
os.chdir('../../')

def plot_model_column(ax,x,var,signi=None,label=' ',c_range=(-0.3,0.3), plot_bool=False, cmap='RdBu', signi_lvl=0.05):
	patches = []
	colors = []
	ax.plot([x-0.5,x-0.5],[-2,15],color='k')
	ax.text(x,13.7,label,ha='center',va='bottom',rotation=90,fontsize=8,weight="bold")

	if c_range == 'maxabs':
		maxabs = np.nanmax(np.abs(np.nanpercentile(var,[0,100])))
		c_range = [-maxabs,maxabs]

	result = []
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

				if signi is not None:
					if signi[model,region] < signi_lvl:
						ax.plot(x+x_shi*1.2,y+y_shi*1.2, marker='.', color='k')

	if plot_bool == False:
		if c_range is None:
			c_range = [np.min(var),np.max(var)]
		y= -0.3
		for x_shi,val in zip([-0.33,0,+0.33],[c_range[0]*0.33,np.mean(c_range),c_range[1]*0.33]):
			polygon = Polygon([(x+x_shi-0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi+y_wi),(x+x_shi-0.33*0.5,y+y_shi+y_wi)], True)
			patches.append(polygon)
			colors.append(val)
			ax.text(x+x_shi,-1.3,round(val,02),ha='center',va='top',rotation=-90,fontsize=8,weight="bold")

	p = PatchCollection(patches, cmap=cmap, alpha=1)
	p.set_array(np.array(colors))
	p.set_clim(c_range)
	im = ax.add_collection(p)

	return c_range

def plot_obs_column(ax,x,var,masks,pval=None,c_range=(-0.3,0.3), label=' ', x_shi=0 ,y_shi=0, cmap='RdBu'):
	patches = []
	colors = []
	for region,y in regions.items():
		if region in masks.keys():
			mask = masks[region].copy()
			if mask.shape != var['JJA'].shape:
				mask = mask.T
			cor = np.array(var['JJA'].values * mask.values).flatten()
			relevant_cells = np.where((mask.flatten()>0) & (np.isfinite(cor)))[0]
			cor = cor[relevant_cells]

			patches.append(plt.Circle((x, y), 0.25))
			colors.append(np.nansum(cor))

			# homogenety = np.sum( np.sign(cor) == np.sign(np.nansum(cor)) ) / float(cor.shape[0])
			# if homogenety >= 0.9:
			# 	ax.plot([x],[y],'*k')

			mask[mask>0] = 1
			pval_ = np.array(pval['JJA'].values * mask.values).flatten()
			signi = np.sum( (np.sign(cor) == np.sign(np.nansum(cor))) & (pval_[relevant_cells] < 0.05) ) / float(cor.shape[0])
			if signi >= 0.5:
				ax.plot([x],[y],'*k')


	p = PatchCollection(patches, cmap=cmap, edgecolor='k', alpha=1)
	p.set_array(np.array(colors))
	p.set_clim(c_range)
	ax.add_collection(p)

	return ax


summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']
exceed_summary = da.read_nc('data/JJA_summary_srex.nc')['exceed_prob']
had_mask = da.read_nc('masks/srex_mask_73x97.nc')
eobs_mask = da.read_nc('masks/srex_mask_EOBS.nc')
drive_summary = da.DimArray( axes = [summary.region, summary.state,['EKE','SPI3','decrease','increase']], dims=['region','state','icon'], dtype=np.int)
drive_summary.values[:,:,:] = 0

state_dict = {
	'warm' : {'EKE':'_mon', 'SPI3':'_mon', 'name':'warm', 'style':'tas', 'excee':'14'},
	'dry' : {'EKE':'_mon', 'SPI3':'_lagged_mon', 'name':'dry', 'style':'pr', 'excee':'14'},
	'dry-warm' : {'EKE':'_mon', 'SPI3':'_lagged_mon', 'name':'dry-warm', 'style':'cpd', 'excee':'14'},
	'5mm' : {'EKE':'_mon', 'SPI3':'_lagged_mon', 'name':'rain', 'style':'pr', 'excee':'7'},
}

model_shifts = {
	'CAM4-2degree':(-0.25,-0.25),
	'ECHAM6-3-LR':(+0.25,-0.25),
	'MIROC5':(+0.25,+0.25),
	'NorESM1':(-0.25,+0.25),
}

style_dict = {'':'correlation', '_lagged':'lagged correlation', '_lagged_mon':'lagged monthly correlation', '_lagged_season':'lagged seasonal correaltion', '_season':'seasonal correaltion' , '_mon':'monthly correaltion'}

bool_styles = {-1:{'c':'green','m':'v'},
				1:{'c':'magenta','m':'^'},
				0:{'c':'w','m':'.'}}

x_wi, y_wi = 0.25, 0.25
regions = {'EAS':1,'TIB':2,'CAS':3,'WAS':4,'MED':5,'CEU':6,'NEU':7,'NAS':8,'ENA':9,'CNA':10,'WNA':11,'CGI':12,'ALA':13}

for state in summary.state:
	details = state_dict[state]
	plt.close('all')
	with PdfPages('plots/table_driver_'+state+'.pdf') as pdf:

		for corWi in ['EKE','SPI3']:
			fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(4,6), dpi=600)
			ax.axis('off')

			x=1
			x += 1
			c_range = plot_model_column(ax,x,var=summary['All-Hist',:,state,corWi,:,'corrcoef'+details[corWi],'JJA'],\
			 					signi=summary['All-Hist',:,state,corWi,:,'p-value'+details[corWi],'JJA'],\
								label=style_dict[details[corWi]]+'\n'+corWi+' - '+details['name'], cmap='PuOr', c_range='maxabs', signi_lvl=0.1)
			if state != 'warm':
				data = da.read_nc('data/EOBS/cor/cor_'+corWi+'_EOBS_'+state+'.nc')
				ax = plot_obs_column(ax, x=x, var=data['corrcoef'+details[corWi]], pval=data['p-value'+details[corWi]], label=' ', masks=eobs_mask, cmap='PuOr', c_range=c_range)
			if state == 'warm':
				data = da.read_nc('data/HadGHCND/All-Hist/cor_EKE_HadGHCND_All-Hist_'+state+'.nc')
				ax = plot_obs_column(ax, x=x, var=data['corrcoef'], pval=data['p_value'], label=' ', masks=had_mask, cmap='PuOr', c_range=c_range)

			x += 1
			rel_diff_corWi = (summary['Plus20-Future',:,state,corWi,:,'mean'+details[corWi].replace('_mon','')+'_'+corWi,'JJA'] - summary['All-Hist',:,state,corWi,:,'mean'+details[corWi].replace('_mon','')+'_'+corWi,'JJA'])# / summary['All-Hist',:,state,corWi,:,'mean_'+corWi,'JJA'] * 100
			rel_diff_corWi[np.isfinite(rel_diff_corWi)==False] = np.nan
			c_range = plot_model_column(ax,x,rel_diff_corWi,label = 'change\nin '+corWi+' []', cmap='PuOr',c_range='maxabs')


			x += 1
			var = (exceed_summary[:,'Plus20-Future',:,details['style']+'_'+state,details['excee']] - exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']]) / exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']] *100
			c_range = plot_model_column(ax,x,var,label = 'rel. change in\nprobability\nof exceeding\n'+details['excee']+' '+details['name']+' days [%]', cmap='PiYG_r', c_range='maxabs')


			drive = rel_diff_corWi / summary['All-Hist',:,state,corWi,:,'corrcoef'+details[corWi],'JJA']
			drive *= np.array(summary['All-Hist',:,state,corWi,:,'p-value'+details[corWi],'JJA'] < 0.1, np.int)
			# var *= np.array(np.abs(rel_diff_corWi) > 1, np.int)
			c_range = plot_model_column(ax,x,drive, label='', plot_bool=True) # ''+corWi+' forcing on\n'+state+' persistence'

			for region,y_reg in regions.items():
				ax.plot([0,x+0.5],[y_reg-0.5,y_reg-0.5],color='gray')
				ax.text(0.2,y_reg,region,va='center',weight='bold',color='gray')
			for region,y_reg in regions.items():

				if np.sum(np.sign(var[:,region]) == np.sign(np.nanmean(var[:,region]))) >= 3 and np.sign(np.nanmean(var[:,region]))!=0:
					ax.text(0.2,y_reg,region,va='center',weight='bold')
					icon = {-1:'decrease', 1:'increase'}[np.sign(np.nanmean(var[:,region]))]
					imscatter(x+1, y_reg, icon_dict[icon], zoom=0.025, ax=ax)
					drive_summary[region,state,icon] = 1

				if np.sum(np.sign(var[:,region] * drive[:,region])) >= 2:
					print('-----------')
					# ax.plot([0.1,x+0.5,x+0.5,0.1,0.1],[y_reg-0.5,y_reg-0.5,y_reg+0.5,y_reg+0.5,y_reg-0.5], linestyle='--', linewidth=3, color='green')
					imscatter(x+1.5, y_reg, icon_dict[corWi], zoom=0.025, ax=ax)
					drive_summary[region,state,corWi] = 1

			ax.plot([0,8.5],[13.5,13.5],color='k')
			# ax.text(0,-1,'scale',va='center',weight='bold')
			ax.text(0,15,"\n".join(textwrap.wrap(details['name']+' persistence',12)),fontsize=9,va='center',weight='bold')


			ax.set_xlim(0,6)
			ax.set_ylim(-1.5,17)

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

da.Dataset({'drive':drive_summary}).write_nc('data/drive_summary.nc')

#
