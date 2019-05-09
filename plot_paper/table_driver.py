import os,sys,glob,time,collections,gc,pickle,textwrap

for home_path in ['/Users/peterpfleiderer/Projects/Persistence','Dokumente/klima_uni/Persistence_small']:
	try:
		os.chdir(home_path)
	except:
		pass

os.chdir('persistence_in_HAPPI/plot_paper')
from __plot_imports import *
os.chdir('../../')


'''
##############################################################################
		MODEL COLUMN
##############################################################################
'''

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
		y= -0.3
		if c_range is None:
			c_range = [np.nanmin(var),np.nanmax(var)]
			for x_shi,val in zip([-0.33,0,+0.33],np.nanpercentile(var,[10,50,90])):
				polygon = Polygon([(x+x_shi-0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi-y_wi),(x+x_shi+0.33*0.5,y+y_shi+y_wi),(x+x_shi-0.33*0.5,y+y_shi+y_wi)], True)
				patches.append(polygon)
				colors.append(val)
				ax.text(x+x_shi,-1.3,round(val,02),ha='center',va='top',rotation=-90,fontsize=8,weight="bold")

		else:
			for x_shi,val in zip([-0.33,+0.33],sorted([c_range[0]*0.33,c_range[1]*0.33])):
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

'''
##############################################################################
		OBS COLUMN
##############################################################################
'''
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

'''
##############################################################################
		STATE CHANGE
##############################################################################
'''
def plot_state_change_table(ax,x0,state,letter):
	details = state_change_dict[state]

	x=x0
	ax.text(x+0.3,14.5,details['name'],fontsize=10,va='center',ha='right',weight='bold')
	ax.text(x,17,letter,fontsize=10,va='center',ha='right',weight='bold')

	# __________________________________
	x += 1
	var = (state_count[:,'JJA',state,:,'All-Hist'] ) *100
	im_state_hist = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('historic fraction of '+details['name']+' days',15)), cmap='Wistia', c_range=None)
	# __________________________________

	# __________________________________
	x += 1
	var = (state_count[:,'JJA',state,:,'Plus20-Future'] - state_count[:,'JJA',state,:,'All-Hist'] ) * 100
	im_state_change = plot_model_column(ax,x,var,label = '\n'.join(textwrap.wrap('change in fraction of '+details['name']+' days',15)), cmap='RdBu_r', c_range='maxabs')

	# __________________________________

	ax.text(x+0.6,16.5,"\n".join(textwrap.wrap('rel. change in probability of exceeding '+details['excee']+' '+details['name']+' days',20)) ,fontsize=8,va='center') # ,weight='bold'
	ax.plot([x+0.5,x+0.5],[0,18],color='k')
	#
	# ax.text(x+1.2,14.8,'added\n'+details['name']+' days\n----------\nprojected\nby GCMs',fontsize=7,va='center',ha='center',rotation=35) # ,weight='bold'

	# __________________________________
	x += 1
	arti = (exceed_summary[:,'Plus20-Artificial-v1',:,details['style']+'_'+state,details['excee']] - exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']]) / exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']] *100
	im_pers = plot_model_column(ax,x,arti,label = '\n'.join(textwrap.wrap('randomly altered '+details['name']+' days',10)), cmap='PiYG_r', c_range=details['c_range'])

	x += 1
	var = (exceed_summary[:,'Plus20-Future',:,details['style']+'_'+state,details['excee']] - exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']]) / exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']] *100
	ks = KS[:,:,state,'All-Hist','Plus20-Future']
	c_range = plot_model_column(ax,x,var, signi=ks, signi_lvl=0.01, label = '\n'.join(textwrap.wrap('projected by GCMs',10)), cmap='PiYG_r', c_range=details['c_range'])
	# __________________________________

	for region,y_reg in regions.items():
		ax.plot([x0,x+0.5],[y_reg-0.5,y_reg-0.5],color='k')
		ax.text(x0-0.5,y_reg,region,va='center',weight='bold',color='k')
	for region,y_reg in regions.items():

		significant_change = ks[:,region] < 0.01
		agreeing_change = np.sign(var[:,region]) == np.sign(np.nanmean(var[:,region]))
		contributing_change = significant_change * agreeing_change
		if np.sum(contributing_change) >= 3 and np.sign(np.nanmean(var[:,region]))!=0:
			ax.text(0.5,y_reg,region,va='center',weight='bold')
			icon = {-1:'decrease', 1:'increase'}[np.sign(np.nanmean(var[:,region]))]
			imscatter(x+1, y_reg, icon_dict[icon]['icon'], zoom=0.025, ax=ax)
			drive_summary[region,state,icon] = 1

		if np.sum(np.sign(var[:,region][contributing_change].values) == np.sign(arti[:,region][contributing_change].values)) >= 3:
			ax.text(0.5,y_reg,region,va='center',weight='bold')
			imscatter(x+1.5, y_reg, icon_dict['rain']['icon'], zoom=0.025, ax=ax)
			drive_state_summary[region,state,'rain'] = 1

	ax.plot([x0,x+1.5],[13.5,13.5],color='k')

'''
##############################################################################
		DRIVER
##############################################################################
'''
def plot_driver_column(ax,x0,state,corWi,letter):
	details = state_dict[state]

	x = x0
	ax.text(x+0.3,14.5,details['name']+'\n'+corWi,fontsize=10,va='center',ha='right',weight='bold')
	ax.text(x,17,letter,fontsize=10,va='center',ha='right',weight='bold')

	x += 1
	cor = summary['All-Hist',:,state,corWi,:,'corrcoef'+details[corWi],'JJA']
	c_range = plot_model_column(ax,x,var=cor,\
	 					signi=summary['All-Hist',:,state,corWi,:,'p-value'+details[corWi],'JJA'],\
						label=style_dict[details[corWi]]+'\n'+corWi+' - '+details['name'], cmap=corWi_dict[corWi]['cmap'], c_range='maxabs', signi_lvl=0.1)
	if state != 'warm':
		data = da.read_nc('data/EOBS/cor/cor_'+corWi+'_EOBS_'+state+'.nc')
		ax = plot_obs_column(ax, x=x, var=data['corrcoef'+details[corWi]], pval=data['p-value'+details[corWi]], label=' ', masks=eobs_mask, cmap=corWi_dict[corWi]['cmap'], c_range=c_range)
	if state == 'warm':
		data = da.read_nc('data/HadGHCND/All-Hist/cor_EKE_HadGHCND_All-Hist_'+state+'.nc')
		ax = plot_obs_column(ax, x=x, var=data['corrcoef'], pval=data['p_value'], label=' ', masks=had_mask, cmap=corWi_dict[corWi]['cmap'], c_range=c_range)

	x += 1
	rel_diff_corWi = (summary['Plus20-Future',:,state,corWi,:,'mean'+details[corWi].replace('_mon','')+'_'+corWi,'JJA'] - summary['All-Hist',:,state,corWi,:,'mean'+details[corWi].replace('_mon','')+'_'+corWi,'JJA'])# / summary['All-Hist',:,state,corWi,:,'mean_'+corWi,'JJA'] * 100
	rel_diff_corWi[np.isfinite(rel_diff_corWi)==False] = np.nan
	c_range = plot_model_column(ax,x,rel_diff_corWi,label = 'change\nin '+corWi+' '+corWi_dict[corWi]['units'], cmap=corWi_dict[corWi]['cmap'],c_range='maxabs')


	x += 1
	var = (exceed_summary[:,'Plus20-Future',:,details['style']+'_'+state,details['excee']] - exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']]) / exceed_summary[:,'All-Hist',:,details['style']+'_'+state,details['excee']] *100
	ks = KS[:,:,state,'All-Hist','Plus20-Future']
	c_range = plot_model_column(ax,x,var, signi=ks, signi_lvl=0.01, label = 'rel. change in probability\nof exceeding\n'+details['excee']+' '+details['name']+' days [%]', cmap='PiYG_r', c_range='maxabs')


	drive = rel_diff_corWi / summary['All-Hist',:,state,corWi,:,'corrcoef'+details[corWi],'JJA']
	drive *= np.array(summary['All-Hist',:,state,corWi,:,'p-value'+details[corWi],'JJA'] < 0.1, np.int)
	c_range = plot_model_column(ax,x,drive, label='', plot_bool=True) # ''+corWi+' forcing on\n'+state+' persistence'

	for region,y_reg in regions.items():
		ax.plot([x0,x+0.5],[y_reg-0.5,y_reg-0.5],color='k')
		ax.text(x0-0.5,y_reg,region,va='center',weight='bold',color='k')
	for region,y_reg in regions.items():

		############
		# Change
		############
		significant_change = ks[:,region] < 0.01
		agreeing_change = np.sign(var[:,region]) == np.sign(np.nanmean(var[:,region]))
		contributing_change = significant_change * agreeing_change
		if np.sum(contributing_change) >= 3 and np.sign(np.nanmean(var[:,region]))!=0:
			icon = {-1:'decrease', 1:'increase'}[np.sign(np.nanmean(var[:,region]))]
			imscatter(x+1, y_reg, icon_dict[icon]['icon'], zoom=0.025*icon_dict[icon]['scale'], ax=ax)
			drive_summary[region,state,icon] = 1

		drive_match = np.sign(var[:,region][contributing_change].values) == np.sign(drive[:,region][contributing_change].values)
		drive_homogenity = np.sign(cor[:,region][contributing_change][drive_match].values) == np.sign(np.nanmean(cor[:,region][contributing_change][drive_match].values))
		if np.sum(drive_match) >= 3 and np.sum(drive_homogenity) >= 3:
			imscatter(x+1.5, y_reg, icon_dict[corWi]['icon'], zoom=0.025*icon_dict[corWi]['scale'], ax=ax)
			drive_summary[region,state,corWi] = 1
			if state not in selection[corWi].keys():
				selection[corWi][state] = [region]
			else:
				selection[corWi][state].append(region)

	ax.plot([x0,x+1.5],[13.5,13.5],color='k')


summary = da.read_nc('data/cor_reg_summary.nc')['summary_cor']
KS = da.read_nc('data/reg_KS-test.nc')['p-value']
period_count = da.read_nc('data/period_count.nc')['period_count']
state_count = da.read_nc('data/state_count_srex.nc')['state_count']
artificial = da.read_nc('data/artificial/reg_summary_mean_qu_artificial.nc')['artificial_summary']
artificial = artificial[:,summary.model]
exceed_summary = da.read_nc('/Users/peterpfleiderer/Projects/Persistence/data/JJA_summary_srex.nc')['exceed_prob']
exceed_artificial = da.read_nc('/Users/peterpfleiderer/Projects/Persistence/data/artificial/JJA_summary_srex_artificial.nc')['exceed_prob']
exceed_summary = da.concatenate((exceed_summary,exceed_artificial),align=True, axis = 'scenario')
for variable in [KS,period_count,exceed_summary]:
	variable = variable[summary.model]

drive_state_summary = da.DimArray( axes = [summary.region, summary.state,['rain']], dims=['region','state','icon'], dtype=np.int)
drive_state_summary.values[:,:,:] = 0

state_change_dict = {
	'dry' : {'c_range':[-15,15], 'name':'dry', 'style':'pr', 'excee':'14'},
	'5mm' : {'c_range':[-30,30], 'name':'rain', 'style':'pr', 'excee':'7'},
}

state_dict = {
	'warm' : {'EKE':'_mon', 'SPI3':'_lagged_mon', 'name':'warm', 'style':'tas', 'excee':'14'},
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

bool_styles = {-1:{'c':'green','m':'v'},
				1:{'c':'magenta','m':'^'},
				0:{'c':'none','m':'.'}}


model_shifts = {
	'CAM4-2degree':(-0.25,-0.25),
	'ECHAM6-3-LR':(+0.25,-0.25),
	'MIROC5':(+0.25,+0.25),
	'NorESM1':(-0.25,+0.25),
}

corWi_dict = {
	'EKE':{'units':'[m2/s2]','cmap':'PuOr'},
	'SPI3':{'units':'','cmap':'BrBG'}
}

style_dict = {'':'correlation', '_lagged':'lagged correlation', '_lagged_mon':'lagged monthly correlation', '_lagged_season':'lagged seasonal correaltion', '_season':'seasonal correaltion' , '_mon':'monthly correaltion'}

bool_styles = {-1:{'c':'green','m':'v'},
				1:{'c':'magenta','m':'^'},
				0:{'c':'w','m':'.'}}

x_wi, y_wi = 0.25, 0.25
regions = {'EAS':1,'TIB':2,'CAS':3,'WAS':4,'MED':5,'CEU':6,'NEU':7,'NAS':8,'ENA':9,'CNA':10,'WNA':11,'CGI':12,'ALA':13}

plt.close('all')
fig,ax = plt.subplots(nrows=1,figsize = (10,8), dpi=600)
ax.axis('off')
plot_driver_column(ax,x0=1,state='dry',corWi='EKE',letter='a')
plot_driver_column(ax,x0=7,state='dry',corWi='SPI3',letter='b')
plot_state_change_table(ax,x0=13,state='dry',letter='c')
ax.set_ylim(-1.5,17.5)
plt.tight_layout()
plt.savefig('plots/table_driver_'+'dry'+'.pdf')

plt.close('all')
fig,ax = plt.subplots(nrows=1,figsize = (10,8), dpi=600)
ax.axis('off')
plot_driver_column(ax,x0=1,state='5mm',corWi='EKE',letter='a')
plot_driver_column(ax,x0=7,state='5mm',corWi='SPI3',letter='b')
plot_state_change_table(ax,x0=13,state='5mm',letter='c')
ax.set_ylim(-1.5,17.5)
plt.tight_layout()
plt.savefig('plots/table_driver_'+'5mm'+'.pdf')

plt.close('all')
fig,ax = plt.subplots(nrows=1,figsize = (6,8), dpi=600)
ax.axis('off')
plot_driver_column(ax,x0=1,state='dry-warm',corWi='EKE',letter='a')
plot_driver_column(ax,x0=7,state='dry-warm',corWi='SPI3',letter='b')
ax.set_ylim(-1.5,17.5)
plt.tight_layout()
plt.savefig('plots/table_driver_'+'dry-warm'+'.pdf')

plt.close('all')
fig,ax = plt.subplots(nrows=1,figsize = (6,8), dpi=600)
ax.axis('off')
plot_driver_column(ax,x0=1,state='warm',corWi='EKE',letter='a')
plot_driver_column(ax,x0=7,state='warm',corWi='SPI3',letter='b')
ax.set_ylim(-1.5,17.5)
plt.tight_layout()
plt.savefig('plots/table_driver_'+'warm'+'.pdf')


#
