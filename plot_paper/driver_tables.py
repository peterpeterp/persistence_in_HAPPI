import os,sys,glob,time,collections,gc,pickle,textwrap

for home_path in ['/Users/peterpfleiderer/Projects/Persistence','Dokumente/klima_uni/Persistence_small']:
	try:
		os.chdir(home_path)
	except:
		pass

sys.path.append('persistence_in_HAPPI/plot_paper')
from __plot_imports import *

def plot_model_column(ax,x,var,signi=None,label=' ',c_range=(-0.3,0.3), plot_bool=False, cmap='RdBu', signi_lvl=0.05):
	patches = []
	colors = []
	ax.plot([x-0.5,x-0.5],[-2,15],color='k')
	ax.text(x,13.7,label,ha='center',va='bottom',rotation=90,fontsize=8,weight="bold")

	if c_range == 'maxabs':
		maxabs = np.max(np.abs(np.nanpercentile(var,[10,90])))
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
						ax.plot(x+x_shi*1.2,y+y_shi*1.2, marker='*', color='k')


		if np.sum(np.sign(var[:,region]) == np.sign(np.nanmean(var[:,region]))) >= 3 and np.sign(np.nanmean(var[:,region]))!=0:
			# ax.plot(x,y, marker='*', color='k')
			result.append(region)


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

	return result


summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']

state_dict = {
	'warm' : {'EKE':'', 'SPI3':'', 'name':'warm'},
	'dry' : {'EKE':'', 'SPI3':'_lagged', 'name':'dry'},
	'dry-warm' : {'EKE':'', 'SPI3':'_lagged', 'name':'dry-warm'},
	'5mm' : {'EKE':'', 'SPI3':'_lagged', 'name':'rain'},
}

model_shifts = {
	'CAM4-2degree':(-0.25,-0.25),
	'ECHAM6-3-LR':(+0.25,-0.25),
	'MIROC5':(+0.25,+0.25),
	'NorESM1':(-0.25,+0.25),
}

style_dict = {'':'correlation', '_lagged':'lagged correlation'}

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
			fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(4,6))
			ax.axis('off')

			x=1
			x += 1
			im_eke = plot_model_column(ax,x,var=summary['All-Hist',:,state,corWi,:,'corrcoef'+details[corWi],'JJA'],\
			 					# signi=summary['All-Hist',:,state,corWi,:,'p-value'+details[corWi],'JJA'],\
								label=style_dict[details[corWi]]+'\n'+corWi+' - '+details['name'], cmap='PuOr', c_range='maxabs')

			x += 1
			rel_diff_corWi = (summary['Plus20-Future',:,state,corWi,:,'mean_'+corWi,'JJA'] - summary['All-Hist',:,state,corWi,:,'mean_'+corWi,'JJA']) / summary['All-Hist',:,state,corWi,:,'mean_'+corWi,'JJA'] * 100
			im_eke = plot_model_column(ax,x,rel_diff_corWi,label = 'rel. change in '+corWi+'', cmap='PuOr',c_range='maxabs')


			x += 1
			var = rel_diff_corWi / summary['All-Hist',:,state,corWi,:,'corrcoef'+details[corWi],'JJA']
			var *= np.array(summary['All-Hist',:,state,corWi,:,'p-value'+details[corWi],'JJA'] < 0.1, np.int)
			var *= np.array(np.abs(rel_diff_corWi) > 1, np.int)
			result = plot_model_column(ax,x,var, label=''+corWi+' forcing on\n'+state+' persistence', plot_bool=True)

			ax.text(0,15,"\n".join(textwrap.wrap('drivers of '+details['name']+' persistence',12)),fontsize=9,va='center',weight='bold')

			for region,y_reg in regions.items():
				ax.plot([0,x+0.5],[y_reg-0.5,y_reg-0.5],color='gray')
				ax.text(0.2,y_reg,region,va='center',weight='bold',color='gray')
			for region,y_reg in regions.items():
				if region in result:
					ax.text(0.2,y_reg,region,va='center',weight='bold')
					ax.plot([0.1,x+0.5,x+0.5,0.1,0.1],[y_reg-0.5,y_reg-0.5,y_reg+0.5,y_reg+0.5,y_reg-0.5], linestyle='-', linewidth=3, color='darkred')

			ax.plot([0,8.5],[13.5,13.5],color='k')
			ax.text(0,-1,'scale',va='center',weight='bold')


			ax.set_xlim(0,6)
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



#
