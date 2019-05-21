import os,sys,glob,time,collections,gc

for home_path in ['/Users/peterpfleiderer/Projects/Persistence','Dokumente/klima_uni/Persistence_small']:
	try:
		os.chdir(home_path)
	except:
		pass

os.chdir('persistence_in_HAPPI/plot')
import __plot_imports; reload(__plot_imports); from __plot_imports import *
os.chdir('../../')

import seaborn as sns
sns.set_style("whitegrid")

sys.path.append('/Users/peterpfleiderer/Projects/git-packages/regional_panels_on_map')
import regional_panels_on_map as regional_panels_on_map; reload(regional_panels_on_map)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

if 'big_dict' not in globals():
	big_dict={}
	for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree','EOBS','HadGHCND']:
		infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
		pkl_file=open(infile, 'rb')
		big_dict[dataset] = pickle.load(pkl_file);	pkl_file.close()


all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.axis('off')

def distrs(subax,region,info_dict):
	print('________'+region+'________')
	for state,details in info_dict.items():
		ensemble=np.zeros([4,35])*np.nan
		nmax=35
		for dataset,i in zip(['MIROC5','ECHAM6-3-LR','CAM4-2degree','NorESM1'],range(4)):
			tmp_h=big_dict[dataset][region]['All-Hist'][state]['JJA']
			count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) * 100 for ii in range(len(tmp_h['count']))])
			nmax=min(nmax,len(count_h))
			ensemble[i,:nmax]=count_h[0:nmax]
		#subax.plot(range(1,nmax+1),np.nanmean(ensemble[:,0:nmax],axis=0),color=color,linestyle=':')
		subax.fill_between(range(1,nmax+1),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=details['color'],alpha=0.3,edgecolor=details['color'])

		if region in ['CEU','NEU','MED']:
			tmp_h=big_dict['EOBS'][region]['All-Hist'][state]['JJA']
			count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) * 100 for ii in range(len(tmp_h['count']))])
			subax.plot(range(1,len(count_h)+1),count_h,color=details['color'],linestyle='-')
			if state=='warm':
				#print('EOBS',style,state)
				print('EOBS',count_h[[7,14,21]])
				#print('EOBS',np.nanargmin(abs(count_h-1)))

	if 'warm' in info_dict.keys():
		tmp_h=big_dict['HadGHCND'][region]['All-Hist']['warm']['JJA']
		count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) * 100 for ii in range(len(tmp_h['count']))])
		subax.plot(range(1,len(count_h)+1),count_h,color=info_dict['warm']['color'], linestyle='--')
		print('HadGHCND',count_h[[7,14,21]])
		#print('HadGHCND',np.nanargmin(abs(count_h-1)))

		if region == 'mid-lat' and False:
			tau = -1/np.log(0.5)
			per_prob = np.exp(-1/tau*np.array(range(30),dtype=np.float)) *100
			per_count = per_prob / per_prob[-1]
			exceed_prob=np.array([np.sum(per_count[ii:])/float(np.sum(per_count)) * 100 for ii in range(len(per_count))])
			subax.plot(range(1,41),exceed_prob,'k--')

	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.95, 0.80), xycoords='axes fraction', color='black', weight='bold', fontsize=10, horizontalalignment='right')

def axis_settings(subax,info_dict,label=False,region=None):
	subax.set_yscale('log')
	subax.set_xlim((0,35))
	subax.set_ylim((0.01,100))
	subax.set_xticks([7,14,21,28,35])
	subax.set_yticks([0.01,0.1,1,10,100])
	if region == 'mid-lat':
		subax.set_xlabel('Period length [days]',fontsize=10)
		subax.set_ylabel('Exceedence probability [%]',fontsize=10)
		subax.tick_params(axis='x',labelsize=10, colors='k',size=1)
		subax.tick_params(axis='y',labelsize=10, colors='k',size=1)
		subax.yaxis.get_label().set_backgroundcolor('w')
		bbox = dict(boxstyle="round", ec="w", fc="w", alpha=1)
		plt.setp(subax.get_yticklabels(), bbox=bbox)
	else:
		subax.set_yticklabels([])
		subax.set_xticklabels([])
	locmin = mticker.LogLocator(base=10, subs=[1.0])
	subax.yaxis.set_minor_locator(locmin)
	subax.yaxis.set_minor_formatter(mticker.NullFormatter())
	subax.yaxis.get_label().set_backgroundcolor('w')
	for tick in subax.yaxis.get_major_ticks():
		tick.label.set_backgroundcolor('w')
	subax.grid(True,which="both",ls="--",c='gray',lw=0.5)

	return(subax)

plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rain'}

info_dict = {
	'warm': {
		'state':'warm', 'name':'warm', 'style':'tas', 'color':'#FF3030', 'c_range':(-15,20), 'letter':'a'
	},
	'dry': {
		'state':'dry', 'name':'dry', 'style':'pr', 'color':'#FF8C00', 'c_range':(-15,20), 'letter':'b'
	},
	'dry-warm': {
		'state':'dry-warm', 'name':'dry-warm', 'style':'cpd', 'color':'#BF3EFF', 'c_range':(-15,20), 'letter':'c'
	},
	'5mm': {
		'state':'5mm', 'name':'rain', 'style':'pr', 'color':'#009ACD', 'c_range':(-50,100), 'letter':'d'
	}
}

plt.close('all')
fig,ax_map=regional_panels_on_map.regional_panels_on_map(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.1, info_dict = info_dict, title=None)

ax_map.annotate('d', xy=(0.01, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=13, backgroundcolor='w')


with sns.axes_style("white"):
	legax = fig.add_axes([0.89,0.01,0.105,0.98], facecolor='w', zorder=4)
legax.axis('off')
legax.set_yticklabels([])
legax.set_xticklabels([])

legend_elements=[]

legend_elements.append(Line2D([0], [0], color='w', label='HAPPI models'))
for state,details in info_dict.items():
	legend_elements.append(Patch(facecolor=details['color'],alpha=0.3, label=state))

legend_elements.append(Line2D([0], [0], color='w', label=''))
legend_elements.append(Line2D([0], [0], color='w', label='HadGHCND'))
legend_elements.append(Line2D([0], [0], color='#FF3030', linestyle='--', label='warm'))

legend_elements.append(Line2D([0], [0], color='w', label=''))
legend_elements.append(Line2D([0], [0], color='w', label='EOBS'))
for state,details in info_dict.items():
	legend_elements.append(Line2D([0], [0], color=details['color'], linestyle='-', label=state))

legax.legend(handles=legend_elements, loc='upper right',fontsize=9,ncol=1, frameon=True, facecolor='w', framealpha=1, edgecolor='w')


plt.tight_layout(); plt.savefig('plots/poster/NH_clim_distrs_poster.png',dpi=600, transparent=True); plt.close()














#
