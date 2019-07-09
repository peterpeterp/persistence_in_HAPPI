import os,sys,glob,time,collections,gc

sys.path.append('/Users/peterpfleiderer/Projects/git-packages/regional_panels_on_map')
import regional_panels_on_map as regional_panels_on_map; reload(regional_panels_on_map)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

os.chdir('persistence_in_HAPPI/plot_paper_final')
import __plot_imports; reload(__plot_imports); from __plot_imports import *
os.chdir('../../')

import seaborn as sns
sns.set_style("whitegrid")
#
from matplotlib import rc
rc('text', usetex=True)

from matplotlib import rcParams
rcParams['font.family'] = "Times New Roman"

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

if 'big_dict' not in globals():
	big_dict={}
	for dataset in ['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree','EOBS','HadGHCND']:
		infile = 'data/'+dataset+'/'+dataset+'_regional_distrs_srex.pkl'
		pkl_file=open(infile, 'rb')
		big_dict[dataset] = pickle.load(pkl_file);	pkl_file.close()

all_regs=NH_regs.copy()

all_regs['mid-lat']['pos'] = (-140,37)

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}



def plot_bar(ax,x,to_plot,color,hatch=None, alpha=0.4, marker='+'):
	ax.fill_between([x-0.1,x+0.1],[np.nanmin(to_plot,axis=0),np.nanmin(to_plot,axis=0)],[np.nanmax(to_plot,axis=0),np.nanmax(to_plot,axis=0)],\
	 color=color, edgecolor='w', hatch=hatch, alpha=alpha)
	#ax.plot([x-0.1,x+0.1],[np.nanmean(to_plot,axis=0),np.nanmean(to_plot,axis=0)],color='k')
	ax.scatter([x],[np.nanmean(to_plot,axis=0)],color='k',marker=marker)



def distrs(subax,region,info_dict):
	print('________'+region+'________')
	for pos,state in enumerate(['warm','dry','dry-warm','5mm']):
		details = info_dict[state]
		for scenario,hatch,marker,shift in zip(['Plus15-Future','Plus20-Future'],['---','///'],['x','+'],[-0.2,0.2]):
			ensemble=np.zeros([4])*np.nan
			nmax=35
			for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
				tmp_fu=big_dict[dataset][region][scenario][state]['JJA']
				tmp_h=big_dict[dataset][region]['All-Hist'][state]['JJA']
				count_fu=np.sum(tmp_fu['count'][details['excee']:])/float(np.sum(tmp_fu['count']))
				count_h=np.sum(tmp_h['count'][details['excee']:])/float(np.sum(tmp_h['count']))
				ensemble[i]= (count_fu - count_h) / count_h * 100.

			plot_bar(subax,pos+shift,ensemble,details['color'],hatch=hatch,marker=marker)


	lb_color ='none'
	if all_regs[region]['edge'] != 'none':
		lb_color = all_regs[region]['edge']
	if all_regs[region]['color'] != 'none':
		lb_color = all_regs[region]['color']
	subax.annotate(region, xy=(0.05, 0.80), xycoords='axes fraction', color='k', weight='bold', fontsize=10)

def axis_settings(subax,info_dict,label=False,region=None):
	subax.set_xlim((-0.5,3.5))
	subax.set_ylim((-10,30))
	subax.set_xticks([0,1,2,3])
	subax.set_xticklabels([info_dict[state]['name']+'\n'+str(info_dict[state]['excee'])+'-days' for state in ['warm','dry','dry-warm','5mm']])
	if region == 'mid-lat':
		subax.set_ylabel('rel. change in\nExceedence probability [\%]',fontsize=10)
		subax.tick_params(axis='x',labelsize=9, colors='k',size=1,rotation=90)
		subax.tick_params(axis='y',labelsize=10, colors='k',size=1)
		subax.yaxis.get_label().set_backgroundcolor('w')
		bbox = dict(boxstyle="round", ec="w", fc="w", alpha=1)
		plt.setp(subax.get_yticklabels(), bbox=bbox)
	else:
		subax.set_yticklabels([])
		subax.set_xticklabels([])
	subax.locator_params(axis = 'y', nbins = 5)
	subax.grid(True,which="both",ls="--",c='gray',lw=0.35)
	subax.axhline(y=0,c='gray')
	return(subax)

info_dict = {
	'warm': {
		'state':'warm', 'name':'warm', 'style':'tas', 'color':'#FF3030', 'excee':14, 'letter':'a'
	},
	'dry': {
		'state':'dry', 'name':'dry', 'style':'pr', 'color':'#FF8C00', 'excee':14, 'letter':'b'
	},
	'dry-warm': {
		'state':'dry-warm', 'name':'dry-warm', 'style':'cpd', 'color':'#BF3EFF', 'excee':14, 'letter':'c'
	},
	'5mm': {
		'state':'5mm', 'name':'rain', 'style':'pr', 'color':'#009ACD', 'excee':7, 'letter':'d'
	}
}

plt.close('all')
fig,ax_map=regional_panels_on_map.regional_panels_on_map(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.1, info_dict = info_dict, title=None)


with sns.axes_style("white"):
	legax = fig.add_axes([0.885,0.01,0.11,0.98], facecolor='w', zorder=100)
plt.setp(legax.spines.values(), color='k', linewidth=2)
legax.set_yticklabels([])
legax.set_xticklabels([])
legax.set_ylim(-4,11)
x,y = 0,10

legax.annotate('ensomble mean',xy=(x-0.2,y),ha='left', va='center', fontsize=9,fontweight='bold')
legax.plot([x+0,x+2],[y-0.5,y-0.5],'k')
y-=1
for scenario,hatch,marker,shift in zip(['$1.5^\circ C$','$2^\circ C$'],['---','///'],['x','+'],[-0.2,0.2]):
	legax.scatter(x,y, marker=marker, color='k')
	legax.annotate(scenario,xy=(x+0.5,y),ha='left', va='center', fontsize=8,fontweight='bold')
	y-=0.7

y-=0.5
legax.annotate('$1.5^\circ C$ model spread',xy=(x-0.2,y),ha='left', va='center', fontsize=9,fontweight='bold')
legax.plot([x+0,x+2],[y-0.5,y-0.5],'k')
y-=1
for pos,state in enumerate(['warm','dry','dry-warm','5mm']):
	details = info_dict[state]
	legax.fill_between([x-0.25,x+0.25],[y+0.25,y+0.25],[y-0.25,y-0.25], hatch='---', edgecolor=details['color'], facecolor=details['color'], alpha=0.3)
	legax.annotate(details['name'],xy=(x+0.5,y),ha='left', va='center', fontsize=8,fontweight='bold')
	y-=1

y-=0.5
legax.annotate('$2^\circ C$ model spread',xy=(x-0.2,y),ha='left', va='center', fontsize=9,fontweight='bold')
legax.plot([x+0,x+2],[y-0.5,y-0.5],'k')
y-=1
for pos,state in enumerate(['warm','dry','dry-warm','5mm']):
	details = info_dict[state]
	legax.fill_between([x-0.25,x+0.25],[y+0.25,y+0.25],[y-0.25,y-0.25], hatch='///', edgecolor=details['color'], facecolor=details['color'], alpha=0.3)
	legax.annotate(details['name'],xy=(x+0.5,y),ha='left', va='center', fontsize=8,fontweight='bold')
	y-=1

plt.tight_layout(); plt.savefig('plots/final/NH_1p5_avoid.pdf'); plt.close()











#
