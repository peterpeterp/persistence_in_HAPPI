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


period_count = da.read_nc('data/period_count.nc')['period_count']
summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']
state_count = da.read_nc('data/state_count_srex.nc')['state_count']
artificial = da.read_nc('data/artificial/reg_summary_mean_qu_artificial.nc')['artificial_summary']
exceed_summary = da.read_nc('/Users/peterpfleiderer/Projects/Persistence/data/JJA_summary_srex.nc')['exceed_prob']
exceed_artificial = da.read_nc('/Users/peterpfleiderer/Projects/Persistence/data/artificial/JJA_summary_srex_artificial.nc')['exceed_prob']
exceed_summary = da.concatenate((exceed_summary,exceed_artificial),align=True, axis = 'scenario')

drive_state_summary = da.DimArray( axes = [summary.region, summary.state,['rain']], dims=['region','state','icon'], dtype=np.int)
drive_state_summary.values[:,:,:] = 0

state_dict = {
	'dry' : {'EKE':'_mon', 'SPI3':'_lagged_mon', 'name':'dry', 'style':'pr', 'excee':'14'},
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

plt.close('all')
with PdfPages('plots/table_driver_state_change.pdf') as pdf:

	for state,details in state_dict.items():

		fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(4,6), dpi=600)
		ax.axis('off')

		x=1
		# __________________________________
		x += 1
		var = (state_count[:,'JJA',state,:,'All-Hist'] ) *100
		im_state_hist = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('historic fraction of '+state+' days',15)), cmap='Wistia', c_range=None)
		# __________________________________

		# __________________________________
		x += 1
		var = (state_count[:,'JJA',state,:,'Plus20-Future'] - state_count[:,'JJA',state,:,'All-Hist'] ) * 100
		im_state_change = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('change in fraction of '+state+' days',15)), cmap='RdBu_r', c_range='maxabs')

		# __________________________________
		x += 1
		var = (period_count[:,:,'Plus20-Future',state,'JJA',0] - period_count[:,:,'All-Hist',state,'JJA',0] ) / period_count[:,:,'All-Hist',state,'JJA',0] *100
		im_state_change = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('rel. change in number of '+state+' periods [%]',15)), cmap='RdBu_r', c_range='maxabs')


		# __________________________________

		ax.text(x+0.6,16.5,"\n".join(textwrap.wrap('rel. change in probability of exceeding '+details['excee']+' '+state+' days',25)) ,fontsize=9,va='center',weight='bold')
		ax.plot([x+0.5,x+0.5],[0,18],color='k')

		# __________________________________
		x += 2
		var = (exceed_summary[:,'Plus20-Future',:,details['style']+'_'+state,details['excee']] - exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']]) / exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']] *100
		c_range = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('projected by GCMs',10)), cmap='PiYG_r', c_range='maxabs')
		# __________________________________

		# __________________________________
		x -= 1
		arti = (exceed_summary[:,'Plus20-Artificial-v1',:,details['style']+'_'+state,details['excee']] - exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']]) / exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']] *100
		im_pers = plot_model_column(ax,x,arti,label = '\n'.join(textwrap.wrap('randomly added (removed) '+state+' days',10)), cmap='PiYG_r', c_range=c_range)
		# __________________________________

		for region,y_reg in regions.items():
			ax.plot([0,x+0.5],[y_reg-0.5,y_reg-0.5],color='gray')
			ax.text(0.2,y_reg,region,va='center',weight='bold',color='gray')
		for region,y_reg in regions.items():


			if np.sum(np.sign(var[:,region]) == np.sign(arti[:,region])) >= 3:
				ax.text(0.2,y_reg,region,va='center',weight='bold')
				imscatter(x+2, y_reg, icon_dict['rain'], zoom=0.025, ax=ax)
				drive_state_summary[region,state,'rain'] = 1



		ax.plot([0,8.5],[13.5,13.5],color='k')
		# ax.text(0,-1,'scale',va='center',weight='bold')
		ax.text(0,15,"\n".join(textwrap.wrap(details['name']+' persistence',12)),fontsize=9,va='center',weight='bold')


		ax.set_xlim(0,8)
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

		p = PatchCollection(patches, cmap='gray', alpha=1)
		p.set_array(np.array(range(4)))
		ax.add_collection(p)

		ax.set_xlim(-1,1)
		ax.set_ylim(-1,1)

		fig.tight_layout(); pdf.savefig(); plt.close()

da.Dataset({'drive':drive_state_summary}).write_nc('data/drive_state_summary.nc')

#
