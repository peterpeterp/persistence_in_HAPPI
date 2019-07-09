import os,sys,glob,time,collections,gc

sys.path.append('/Users/peterpfleiderer/Projects/git-packages/regional_panels_on_map')
import regional_panels_on_map as regional_panels_on_map; reload(regional_panels_on_map)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

os.chdir('persistence_in_HAPPI/plot_paper_final')
import __plot_imports; reload(__plot_imports); from __plot_imports import *
os.chdir('../../')

import seaborn as sns
sns.set_style("whitegrid")


pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

if 'big_dict' not in globals():
	big_dict={}
	for dataset in ['CAM4-2degree','MIROC5','NorESM1','ECHAM6-3-LR']:
		infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
		pkl_file=open(infile, 'rb')
		big_dict[dataset] = pickle.load(pkl_file);	pkl_file.close()


		infile = 'data/artificial/'+dataset+'_regional_distrs_srex_artificial.pkl'
		pkl_file=open(infile, 'rb')
		tmp = pickle.load(pkl_file);	pkl_file.close()
		for region in tmp.keys():
			big_dict[dataset][region]['Plus20-Artificial-v1'] = tmp[region]['Plus20-Artificial-v1']

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

#colors=['black']+sns.color_palette("colorblind", 4)

def distrs(subax,region,info_dict):
	state = info_dict['state']
	color = info_dict['color']
	color2 = info_dict['color2']

	ensemble=np.zeros([4,35])*np.nan
	ensemble_arti=np.zeros([4,35])*np.nan
	nmax=35
	for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
		tmp_arti=big_dict[dataset][region]['Plus20-Artificial-v1'][state]['JJA']
		tmp_20=big_dict[dataset][region]['Plus20-Future'][state]['JJA']
		tmp_h=big_dict[dataset][region]['All-Hist'][state]['JJA']
		count_arti=np.array([np.sum(tmp_arti['count'][ii:])/float(np.sum(tmp_arti['count'])) for ii in range(len(tmp_arti['count']))])
		count_20=np.array([np.sum(tmp_20['count'][ii:])/float(np.sum(tmp_20['count'])) for ii in range(len(tmp_20['count']))])
		count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) for ii in range(len(tmp_h['count']))])
		nmax=min(len(count_20),len(count_h),len(count_arti),nmax)
		ensemble[i,:nmax]=(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100
		ensemble_arti[i,:nmax]=(count_arti[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100

	subax.plot(range(1,nmax+1),np.nanmean(ensemble[:,0:nmax],axis=0),color=color,linestyle='-')
	subax.fill_between(range(1,nmax+1),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=color, edgecolor=color,alpha=0.3)

	subax.plot(range(1,nmax+1),np.nanmean(ensemble_arti[:,0:nmax],axis=0),color=color2,linestyle='-')
	subax.fill_between(range(1,nmax+1),np.nanmin(ensemble_arti[:,0:nmax],axis=0),np.nanmax(ensemble_arti[:,0:nmax],axis=0),facecolor=color2, edgecolor=color2,alpha=0.3)

	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.05, 0.05), xycoords='axes fraction', color='black', weight='bold', fontsize=10)

def axis_settings(subax,info_dict,label=False,region=None):
	subax.set_xlim((0,35))
	subax.set_ylim(info_dict['c_range'])
	subax.plot([0,35],[0,0],'k')
	subax.set_xticks(np.arange(7,42,7))
	if region == 'mid-lat':
		subax.set_xticklabels(['7','14','21','35'])
		subax.set_xlabel('Period length [days]',fontsize=10)
		subax.set_ylabel('rel. change in\nExceedence probability [\%]',fontsize=10)
		subax.tick_params(axis='x',labelsize=10, colors='k',size=1)
		subax.tick_params(axis='y',labelsize=10, colors='k',size=1)
		subax.yaxis.get_label().set_backgroundcolor('w')
		bbox = dict(boxstyle="round", ec="w", fc="w", alpha=1)
		plt.setp(subax.get_yticklabels(), bbox=bbox)
	else:
		subax.set_yticklabels([])
		subax.set_xticklabels([])
	subax.locator_params(axis = 'y', nbins = 5)
	subax.grid(True,which="both",ls="--",c='gray',lw=0.35)
	return(subax)

plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rain'}


info_dicts = {
	'dry': {
		'state':'dry', 'name':'dry', 'style':'pr', 'color':'#FF8C00', 'color2':'red', 'c_range':(-15,20), 'letter':'a'
	},
	'5mm': {
		'state':'5mm', 'name':'rain', 'style':'pr', 'color':'#009ACD', 'color2':'blue', 'c_range':(-50,100), 'letter':'b'
	}
}

for name,info_dict in info_dicts.items():
	print('Region\t7-day %s period\t14-day %s period\t21-day %s period' %(name,name,name))

	plt.close('all')
	fig,ax_map=regional_panels_on_map.regional_panels_on_map(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.1, info_dict = info_dict, title=None)

	ax_map.annotate(info_dict['letter'], xy=(0.01, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=13)

	legax = fig.add_axes([0.85,0.0,0.145,0.9], zorder=100)
	legax.axis('off')

	legend_elements=[]
	legend_elements.append(Line2D([0], [0], color='w', linestyle='--', label='ensemble mean'))
	legend_elements.append(Patch(facecolor='w', alpha=0.3, label='model spread'))

	legend_elements.append(Line2D([0], [0], color=info_dict['color'], linestyle='-', label=' '))
	legend_elements.append(Patch(facecolor=info_dict['color'],alpha=0.3, label=' '))

	legend_elements.append(Line2D([0], [0], color=info_dict['color2'], linestyle='-', label=' '))
	legend_elements.append(Patch(facecolor=info_dict['color2'],alpha=0.3, label=' '))

	legax.legend(handles=legend_elements ,title='                                '+info_dict['name']+'    artificial', loc='lower right',fontsize=9,ncol=3, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)

	plt.tight_layout(); plt.savefig('plots/final/NH_changes_artificial_'+info_dict['letter']+'.pdf'); plt.close()



region = 'MED'
tmp_arti=big_dict['CAM4-2degree'][region]['Plus20-Artificial-v1']['dry']['JJA']
tmp_20=big_dict['CAM4-2degree'][region]['Plus20-Future']['dry']['JJA']
tmp_h=big_dict['CAM4-2degree'][region]['All-Hist']['dry']['JJA']
maxlen = min([len(tmp_20['count']),len(tmp_h['count']),len(tmp_arti['count'])])
print(tmp_20['count'][:maxlen] - tmp_h['count'][:maxlen])
print(tmp_arti['count'][:maxlen] - tmp_h['count'][:maxlen])
print(tmp_arti['count'][:maxlen] - tmp_20['count'][:maxlen])

print(sum(tmp_h['count']))
print(sum(tmp_arti['count']))
print(sum(tmp_20['count']))




#
