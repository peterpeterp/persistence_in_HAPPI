import os,sys,glob,time,collections,gc,pickle,textwrap

for home_path in ['/Users/peterpfleiderer/Projects/Persistence','Dokumente/klima_uni/Persistence_small']:
	try:
		os.chdir(home_path)
	except:
		pass

os.chdir('persistence_in_HAPPI/plot_paper')
import __plot_imports; reload(__plot_imports); from __plot_imports import *
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

	if signi is not None:
		for region,y in regions.items():
			for model in model_shifts.keys():
				x_shi,y_shi = model_shifts[model]
				if signi[model,region] > signi_lvl:
					# ax.plot(x+x_shi*1.2,y+y_shi*1.2, marker='.', color='k')
					ax.fill_between([x+x_shi-x_wi,x+x_shi+x_wi],[y+y_shi-y_wi,y+y_shi-y_wi],[y+y_shi+y_wi,y+y_shi+y_wi], edgecolor='gray', hatch='////', facecolor='none', linewidth=0.0)

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

KS = da.read_nc('data/reg_KS-test.nc')['p-value']
KS = KS[summary.model]

exceed_summary = da.read_nc('data/JJA_summary_srex.nc')['exceed_prob']
exceed_summary = exceed_summary[summary.model]

had_mask = da.read_nc('masks/srex_mask_73x97.nc')
eobs_mask = da.read_nc('masks/srex_mask_EOBS.nc')

avoid_summary = da.DimArray( axes = [summary.region, summary.state,['avoided','mitigated','decrease_red','increase_red']], dims=['region','state','icon'], dtype=np.int)
avoid_summary.values[:,:,:] = 0

state_dict = {
	'warm' : {'EKE':'_mon', 'SPI3':'_mon', 'name':'warm', 'style':'tas', 'excee':'14', 'letter':'a'},
	'dry' : {'EKE':'_mon', 'SPI3':'_lagged_mon', 'name':'dry', 'style':'pr', 'excee':'14', 'letter':'b'},
	'dry-warm' : {'EKE':'_mon', 'SPI3':'_lagged_mon', 'name':'dry-warm', 'style':'cpd', 'excee':'14', 'letter':'c'},
	'5mm' : {'EKE':'_mon', 'SPI3':'_lagged_mon', 'name':'rain', 'style':'pr', 'excee':'7', 'letter':'d'},
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
				0:{'c':'none','m':'.'}}

x_wi, y_wi = 0.25, 0.25
regions = {'EAS':1,'TIB':2,'CAS':3,'WAS':4,'MED':5,'CEU':6,'NEU':7,'NAS':8,'ENA':9,'CNA':10,'WNA':11,'CGI':12,'ALA':13}

plt.close('all')
with PdfPages('plots/table_avoided_1p5.pdf') as pdf:
	for state in summary.state:
		details = state_dict[state]

		fig,ax  = plt.subplots(nrows=1,ncols=1,figsize=(2.5,6), dpi=600)
		ax.axis('off')

		x=1
		x += 1
		var20 = (exceed_summary[:,'Plus20-Future',:,details['style']+'_'+state,details['excee']] - exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']]) / exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']] *100
		ks20 = KS[:,:,state,'All-Hist','Plus20-Future']
		c_range = plot_model_column(ax,x,var20, signi=ks20, signi_lvl=0.01, label = 'rel. change in\nexceedance prob.\n$2^\circ$ vs historic', cmap='PiYG_r', c_range='maxabs')

		x += 1
		var15 = (exceed_summary[:,'Plus15-Future',:,details['style']+'_'+state,details['excee']] - exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']]) / exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']] *100
		ks15 = KS[:,:,state,'All-Hist','Plus15-Future']
		c_range = plot_model_column(ax,x,var15, signi=ks15, signi_lvl=0.01, label = 'rel. change in\nexceedance prob.\n$1.5^\circ$ vs historic', cmap='PiYG_r', c_range=c_range)

		for region,y_reg in regions.items():
			ax.plot([0,x+0.5],[y_reg-0.5,y_reg-0.5],color='gray')
			ax.text(0.5,y_reg,region,va='center',weight='bold',color='gray')
		for region,y_reg in regions.items():
			############
			# Change
			############
			change15,change20 = 0,0
			significant_change = ks20[:,region] < 0.01
			agreeing_change = np.sign(var20[:,region]) == np.sign(np.nanmean(var20[:,region]))
			contributing_change = significant_change * agreeing_change
			if np.sum(contributing_change) >= 3 and np.sign(np.nanmean(var20[:,region]))!=0:
				ax.text(0.5,y_reg,region,va='center',weight='bold')
				icon = {-1:'decrease', 1:'increase'}[np.sign(np.nanmean(var20[:,region]))]
				imscatter(x+1, y_reg, icon_dict[icon], zoom=0.025, ax=ax)
				change20 = np.nanmean(var20[:,region])

			significant_change = ks15[:,region] < 0.01
			agreeing_change = np.sign(var15[:,region]) == np.sign(np.nanmean(var15[:,region]))
			contributing_change = significant_change * agreeing_change
			if np.sum(contributing_change) >= 3 and np.sign(np.nanmean(var15[:,region]))!=0:
				ax.text(0.5,y_reg,region,va='center',weight='bold')
				icon = {-1:'decrease', 1:'increase'}[np.sign(np.nanmean(var15[:,region]))]
				# imscatter(x+2, y_reg, icon_dict[icon], zoom=0.025, ax=ax)
				change15 = np.nanmean(var15[:,region])

			if np.sign(change15) != np.sign(change20) and np.sign(change20)!=0:
				imscatter(x+1, y_reg, icon_dict['avoided'], zoom=0.025, ax=ax)
				avoid_summary[region,state,'avoided'] = 1

			if np.sign(change20) == 0 and np.sign(change15) != np.sign(change20):
				imscatter(x+1, y_reg, icon_dict[{-1:'decrease_red', 1:'increase_red'}[np.sign(change15)]], zoom=0.025, ax=ax)
				avoid_summary[region,state,{-1:'decrease_red', 1:'increase_red'}[np.sign(change15)]] = 1

			if np.sign(change20) != 0 and np.sign(change15) == np.sign(change20) and change20/change15 > 2:
				imscatter(x+1, y_reg, icon_dict['mitigated'], zoom=0.025, ax=ax)
				print(change20,change15)
				avoid_summary[region,state,'mitigated'] = 1


		ax.plot([0,8.5],[13.5,13.5],color='k')
		# ax.text(0,-1,'scale',va='center',weight='bold')
		ax.text(1.4,13.7,"\n".join(textwrap.wrap(details['excee']+'-day '+details['name']+' periods',10)),fontsize=8,va='bottom', ha='right',weight='bold', rotation=0)
		# ax.text(1.5,13.7,"\n".join(textwrap.wrap('rel. change in exceedance probabilites of '+details['excee']+'-day '+details['name']+' periods',20)),fontsize=8,va='bottom', ha='right',weight='bold', rotation=90)


		ax.set_xlim(0.8,4)
		ax.set_ylim(-1.5,17)
		ax.annotate(details['letter'], xy=(0.0,1), xycoords='axes fraction', fontsize=10, va='center', weight='bold')


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

da.Dataset({'drive':avoid_summary}).write_nc('data/drive_avoided_summary.nc')

#
