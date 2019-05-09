import os,sys,glob,time,collections,gc

sys.path.append('/Users/peterpfleiderer/Projects/allgemeine_scripte')
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

os.chdir('persistence_in_HAPPI/plot_paper')
import __plot_imports; reload(__plot_imports); from __plot_imports import *
os.chdir('../../')

sns.set_style("white")

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

NH_regs={'ALA':{'color':'darkgreen','pos_off':(+40,+3),'summer':'JJA','winter':'DJF'},
		'WNA':{'color':'darkblue','pos_off':(-6,-8),'summer':'JJA','winter':'DJF'},
		'CNA':{'color':'gray','pos_off':(+8,-8),'summer':'JJA','winter':'DJF'},
		'ENA':{'color':'darkgreen','pos_off':(+23,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'color':'darkgreen','pos_off':(-23,+5),'summer':'JJA','winter':'DJF'},
		'CEU':{'color':'darkblue','pos_off':(+4,+7),'summer':'JJA','winter':'DJF'},
		'CAS':{'color':'darkgreen','pos_off':(-5,+13),'summer':'JJA','winter':'DJF'},
		'NAS':{'color':'gray','pos_off':(-13,+11),'summer':'JJA','winter':'DJF'},
		'TIB':{'color':'darkcyan','pos_off':(-15,-16),'summer':'JJA','winter':'DJF'},
		'EAS':{'color':'darkgreen','pos_off':(-13,0),'summer':'JJA','winter':'DJF'},

		'MED':{'color':'gray','pos_off':(-20,-10),'summer':'JJA','winter':'DJF'},
		'WAS':{'color':'darkcyan','pos_off':(-16,-10),'summer':'JJA','winter':'DJF'},
		# 'mid-lat':{'edge':'darkgreen','color':'none','alpha':1,'pos':(-143,27),'summer':'JJA','winter':'DJF','scaling_factor':1.1}
}

all_regs=NH_regs.copy()


polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.axis('off')

def axis_settings(subax,label=False,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None,region=None):
	subax.set_xlim(-2,2)
	subax.set_ylim(-2,2)
	subax.set_yticklabels([])
	subax.set_xticklabels([])
	return(subax)

def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	print('________'+region+'________')
	patches,colors = [], []
	for state,details in state_details.items():
		x,y = details['x'],details['y']
		pc = PatchCollection([matplotlib.patches.Polygon([(x-1.0,y-1.0),(x+1.0,y-1.0),(x+1.0,y+1.0),(x-1.0,y+1.0)])], color=details['color'], edgecolor="k", alpha=0.5, lw=0.5)
		subax.add_collection(pc)
		# pc = PatchCollection([matplotlib.patches.Polygon([(x-0.58,y-0.58),(x+0.58,y-0.58),(x+0.58,y+0.58),(x-0.58,y+0.58)])], color='white', edgecolor="w", alpha=1, lw=0.5)
		# subax.add_collection(pc)

		if region=='mid-lat':
			subax.annotate(legend_dict[state],xy=(x*1.9,y*1.8),ha={-1:'left',1:'right'}[x], va='center', fontsize=8,fontweight='bold')

	if region!='mid-lat':
		for state,details in state_details.items():
			drivers=arg1[region,state,['EKE','SPI3','rain']]
			drivers = drivers.icon[drivers == 1]
			print(region,state,drivers)

			change = arg1[region,state,['decrease','increase']]
			if np.max(change) != 0:
				imscatter(state_details[state]['x']*0.7, state_details[state]['y']*0.9, icon_dict[change.icon[change==1][0]], zoom=0.03, ax=subax)
			else:
				x,y = details['x'],details['y']
				pc = PatchCollection([matplotlib.patches.Polygon([(x-1.0,y-1.0),(x+1.0,y-1.0),(x+1.0,y+1.0),(x-1.0,y+1.0)])], color='white', edgecolor="k", alpha=0.8, lw=0.5)
				subax.add_collection(pc)

			change = arg1[region,state,['decrease_red','increase_red','avoided','mitigated']]
			if np.max(change) != 0:
				icon = change.icon[change==1][0]
				if icon in ['avoided','mitigated']:
					imscatter(state_details[state]['x']*0.7-0.15, state_details[state]['y']*0.9, icon_dict[icon], zoom=0.03, ax=subax)
				else:
					imscatter(state_details[state]['x']*0.7, state_details[state]['y']*0.9, icon_dict[icon], zoom=0.03, ax=subax)

			if len(drivers)>0:
				for icon,xx,yy in zip(drivers,{1:[1.5],2:[1.2,1.6],3:[0.9,1.5,1.6]}[len(drivers)],{1:[1.2],2:[1.5,0.8],3:[1.6,0.7,1.6]}[len(drivers)]):
					imscatter(state_details[state]['x']*xx, state_details[state]['y']*yy, icon_dict[icon], zoom=0.035 * (1/float(len(drivers)))**0.3, ax=subax)


	# for state,icons in arg1[region].items():
	# 	drivers=icons['drive']
	# 	if len(drivers)>0:
	# 		for icon,xx,yy in zip(drivers,{1:[0],2:[-0.33,0.33],3:[-0.5,0,0.5]}[len(drivers)],{1:[0],2:[0,0],3:[-0.33,0.33,-0.33]}[len(drivers)]):
	# 			imscatter(state_details[state]['x']*0.8+xx, state_details[state]['y']*1.2+yy, icon_dict[icon], zoom=0.025 * (1/float(len(drivers)))**0.5, ax=subax)
	#
	# 	if icons['change'] != 'none':
	# 		imscatter(state_details[state]['x']*1.65, state_details[state]['y']*0.5, icon_dict[icons['change']], zoom=0.02, ax=subax)

	subax.annotate(region, xy=(0.5, 0.5), xycoords='axes fraction', color='k', weight='bold', fontsize=8, ha='center', va='center', backgroundcolor='w')


plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rain'}

state_details = {
	'warm':{'x':-1,'y':1,'color':'#FF3030'},
	'dry':{'x':1,'y':1,'color':'#FF8C00'},
	'dry-warm':{'x':-1,'y':-1,'color':'#BF3EFF'},
	'5mm':{'x':1,'y':-1,'color':'#009ACD'},
}

arg1 = da.read_nc('data/drive*summary.nc',align=True, axis='icon')['drive']


fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-150,180], y_ext=[0,85], small_plot_size=0.1, legend_plot=legend_plot, legend_pos=[-160,20], \
	arg1=arg1,
	title=None)

legax = fig.add_axes([0.85,0.2,0.145,0.78])
legax.set_yticklabels([])
legax.set_xticklabels([])
x,y = 0,15

legax.annotate('Persistence',xy=(x,y),ha='left', va='center', fontsize=8,fontweight='bold')
legax.plot([x+0,x+4.5],[y-0.5,y-0.5],'k')
y-=1.5
for state,details in state_details.items():
	pc = PatchCollection([matplotlib.patches.Polygon([(x-0.5,y-0.7),(x+0.5,y-0.7),(x+0.5,y+0.7),(x-0.5,y+0.7)])], color=details['color'], edgecolor="k", alpha=0.5, lw=0.5)
	legax.add_collection(pc)
	legax.annotate(legend_dict[state],xy=(1,y),ha='left', va='top', fontsize=7,fontweight='bold')
	y-=1.5

y-=1
legax.annotate('Driver',xy=(x,y),ha='left', va='center', fontsize=8,fontweight='bold')
legax.plot([x+0,x+4.5],[y-0.5,y-0.5],'k')
y-=1.5
for icon_name,icon_realname in zip(['EKE','SPI3','rain'],['EKE','SPI3','\nchange in\nnumber of\nrain/dry days']):
	imscatter(x, y, icon_dict[icon_name], zoom=0.025, ax=legax)
	legax.annotate(icon_realname,xy=(x+1,y),ha='left', va='center', fontsize=7,fontweight='bold')
	y-=1.5

x,y = 6,15
legax.annotate('Change $2^\circ C$',xy=(x,y),ha='left', va='center', fontsize=8,fontweight='bold')
legax.plot([x+0,x+4.5],[y-0.5,y-0.5],'k')
y-=1.5
for icon_name,icon_realname in zip(['increase','decrease'],['increase','decrease']):
	imscatter(x, y, icon_dict[icon_name], zoom=0.025, ax=legax)
	legax.annotate(icon_realname,xy=(x+1,y),ha='left', va='center', fontsize=7,fontweight='bold')
	y-=1.5

y-=1
legax.annotate('Change $1.5^\circ C$',xy=(x,y),ha='left', va='center', fontsize=8,fontweight='bold')
# y-=0.5
legax.plot([x+0,x+4.5],[y-0.5,y-0.5],'k')
y-=1.5
for icon_name,icon_realname in zip(['increase_red','decrease_red','avoided','mitigated'],['increase','decrease','avoided','mitigated']):
	imscatter(x, y, icon_dict[icon_name], zoom=0.025, ax=legax)
	legax.annotate(icon_realname,xy=(x+1,y),ha='left', va='center', fontsize=7,fontweight='bold')
	y-=1.5

# legax.axhline(y=5.5,color='k')

legax.set_xlim(-1,12)
legax.set_ylim(0,16)

plt.savefig('plots/NH_summary_drive.png',dpi=600)



#
