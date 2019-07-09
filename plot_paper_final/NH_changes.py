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

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

#colors=['black']+sns.color_palette("colorblind", 4)

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.axis('off')
	legend_elements=[]
	# legend_elements.append(Line2D([0], [0], color='w', label=' '))
	#legend_elements.append(Line2D([0], [0], color='w', label='HadGHCND'))
	legend_elements.append(Line2D([0], [0], color='w', linestyle='--', label='ensemble mean'))
	legend_elements.append(Patch(facecolor='w', alpha=0.3, label='model spread'))
	for style,state,color in zip(arg2,arg3,arg4):
		# legend_elements.append(Line2D([0], [0], color='w', label=state))
		#legend_elements.append(Line2D([0], [0], color=color, label=' '))
		legend_elements.append(Line2D([0], [0], color=color, linestyle='-', label=' '))
		legend_elements.append(Patch(facecolor=color,alpha=0.3, label=' '))


	subax.legend(handles=legend_elements ,title='                                       '+'      '.join([legend_dict[aa]+''.join([' ']*int(6/len(aa))) for aa in arg3]), loc='lower right',fontsize=9,ncol=len(arg3)+1, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)

def distrs(subax,region,info_dict):
	ensemble=np.zeros([4,35])*np.nan
	nmax=35
	for dataset,i in zip(['MIROC5','NorESM1','ECHAM6-3-LR','CAM4-2degree'],range(4)):
		tmp_20=big_dict[dataset][region]['Plus20-Future'][info_dict['state']]['JJA']
		tmp_h=big_dict[dataset][region]['All-Hist'][info_dict['state']]['JJA']
		count_20=np.array([np.sum(tmp_20['count'][ii:])/float(np.sum(tmp_20['count'])) for ii in range(len(tmp_20['count']))])
		count_h=np.array([np.sum(tmp_h['count'][ii:])/float(np.sum(tmp_h['count'])) for ii in range(len(tmp_h['count']))])
		nmax=min(len(count_20),len(count_h),nmax)
		tmp=(count_20[0:nmax]-count_h[0:nmax])/count_h[0:nmax]*100
		ensemble[i,:nmax]=tmp

	subax.plot(range(1,nmax+1),np.nanmean(ensemble[:,0:nmax],axis=0),color=info_dict['color'],linestyle='-')
	subax.fill_between(range(1,nmax+1),np.nanmin(ensemble[:,0:nmax],axis=0),np.nanmax(ensemble[:,0:nmax],axis=0),facecolor=info_dict['color'], edgecolor=info_dict['color'],alpha=0.3)

	print('%s\t%0.2f (%0.2f to %0.2f)\t%0.2f (%0.2f to %0.2f)\t%0.2f (%0.2f to %0.2f)' %(region, np.nanmean(ensemble[:,7],axis=0), np.nanmin(ensemble[:,7],axis=0), np.nanmax(ensemble[:,7],axis=0), np.nanmean(ensemble[:,14],axis=0), np.nanmin(ensemble[:,14],axis=0), np.nanmax(ensemble[:,14],axis=0), np.nanmean(ensemble[:,21],axis=0), np.nanmin(ensemble[:,21],axis=0), np.nanmax(ensemble[:,21],axis=0)))
	# print('%s\t%0.2f (%0.2f, %0.2f, %0.2f, %0.2f)\t%0.2f (%0.2f, %0.2f, %0.2f, %0.2f)\t%0.2f (%0.2f, %0.2f, %0.2f, %0.2f)' %(region, np.nanmean(ensemble[:,7],axis=0), np.sort(ensemble[:,7])[0], np.sort(ensemble[:,7])[1], np.sort(ensemble[:,7])[2], np.sort(ensemble[:,7])[3], np.nanmean(ensemble[:,14],axis=0), np.sort(ensemble[:,14])[0], np.sort(ensemble[:,14])[1], np.sort(ensemble[:,14])[2], np.sort(ensemble[:,14])[3], np.nanmean(ensemble[:,21],axis=0), np.sort(ensemble[:,21])[0], np.sort(ensemble[:,21])[1], np.sort(ensemble[:,21])[2], np.sort(ensemble[:,21])[3]))

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


info_dicts = {
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

for name,info_dict in info_dicts.items():
	print('Region\t7-day %s period\t14-day %s period\t21-day %s period' %(name,name,name))

	plt.close('all')
	fig,ax_map=regional_panels_on_map.regional_panels_on_map(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.1, info_dict = info_dict, title=None)

	ax_map.annotate(info_dict['letter'], xy=(0.01, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=13)


	legax = fig.add_axes([0.85,0.05,0.145,0.9], zorder=100)
	legax.axis('off')
	legend_elements=[]
	legend_elements.append(Line2D([0], [0], color=info_dict['color'], linestyle='-', label='ensemble mean'))
	legend_elements.append(Patch(facecolor=info_dict['color'],alpha=0.3, label='model spread'))

	legax.legend(handles=legend_elements ,title=info_dict['name']+' persistence', loc='upper right',fontsize=10,ncol=1, frameon=True, facecolor='w', framealpha=1, edgecolor='w').set_zorder(1)


	plt.tight_layout(); plt.savefig('plots/final/NH_changes_'+name+'.pdf'); plt.close()




'''

Region	7-day dry period	14-day dry period	21-day dry period
ALA	-4.24 (-9.05, -5.54, -3.77, 1.38)	-5.52 (-13.18, -6.18, -5.97, 3.24)	-7.90 (-17.57, -10.48, -6.81, 3.24)
CAS	0.41 (-0.39, 0.27, 0.78, 0.98)	0.39 (-1.27, 0.12, 1.25, 1.46)	0.71 (-1.17, 0.90, 1.33, 1.80)
CEU	4.59 (-0.72, 1.34, 7.39, 10.34)	7.95 (-1.79, 3.49, 13.24, 16.84)	10.18 (-5.77, 6.24, 19.18, 21.06)
CGI	-3.94 (-5.19, -5.01, -2.78, -2.76)	-6.71 (-9.44, -8.54, -5.36, -3.49)	-9.09 (-13.39, -11.71, -7.32, -3.94)
CNA	7.26 (-1.32, 3.30, 11.00, 16.07)	13.43 (-0.99, 6.10, 11.86, 36.75)	15.12 (0.83, 6.08, 7.90, 45.69)
EAS	0.47 (-2.82, -2.56, 2.84, 4.42)	-2.08 (-10.16, -6.25, 1.06, 7.05)	-6.10 (-18.29, -10.19, -3.18, 7.27)
ENA	4.30 (-0.28, 4.92, 6.02, 6.53)	13.35 (7.97, 13.22, 14.43, 17.77)	26.00 (21.07, 23.43, 28.86, 30.64)
MED	3.36 (-0.05, 0.34, 3.39, 9.78)	5.32 (-0.56, 1.12, 4.44, 16.29)	6.70 (-1.21, 1.94, 5.21, 20.89)
NAS	3.38 (0.78, 2.55, 4.65, 5.52)	5.00 (0.16, 2.80, 8.41, 8.66)	6.02 (0.91, 3.00, 9.66, 10.51)
NEU	0.56 (-1.49, -0.54, 1.54, 2.73)	2.81 (-0.07, 2.59, 3.65, 5.09)	5.38 (1.89, 3.83, 7.63, 8.18)
TIB	1.77 (0.07, 1.57, 2.53, 2.91)	1.14 (-0.23, 0.19, 0.65, 3.96)	0.72 (-2.41, -1.29, 2.17, 4.41)
WAS	1.28 (0.77, 0.93, 1.35, 2.08)	1.66 (-0.15, 0.89, 2.84, 3.06)	1.86 (-0.56, 0.16, 3.52, 4.32)
WNA	1.07 (-2.37, 0.68, 1.55, 4.42)	0.84 (-2.69, -1.23, 1.33, 5.95)	-0.74 (-7.41, -1.08, 0.03, 5.48)
mid-lat	2.61 (1.11, 1.84, 3.27, 4.21)	3.08 (-0.10, 1.89, 5.14, 5.39)	2.74 (-1.17, 0.92, 5.47, 5.73)

Region	7-day 5mm period	14-day 5mm period	21-day 5mm period
ALA	17.33 (7.70, 8.21, 21.30, 32.12)	17.93 (-38.16, -11.79, 32.78, 88.91)	128.64 (-25.29, 282.58, nan, nan)
CAS	-7.43 (-16.62, -12.43, -4.98, 4.32)	-12.22 (-26.29, -22.69, -21.06, 21.17)	-20.28 (-42.57, 2.01, nan, nan)
CEU	17.65 (-0.14, 9.33, 27.10, 34.29)	43.76 (11.16, 14.34, 28.77, 120.79)	nan (nan, nan, nan, nan)
CGI	17.37 (3.04, 10.61, 25.97, 29.87)	58.62 (-26.15, 78.33, 90.22, 92.06)	nan (nan, nan, nan, nan)
CNA	8.14 (-3.47, 0.98, 17.28, 17.77)	-0.71 (-49.91, -4.69, 19.18, 32.57)	nan (nan, nan, nan, nan)
EAS	13.34 (4.47, 12.94, 13.04, 22.93)	16.79 (3.60, 10.37, 23.70, 29.49)	18.93 (3.49, 6.61, 32.71, 32.92)
ENA	11.28 (8.00, 8.85, 10.84, 17.44)	8.64 (-15.08, 11.28, 11.33, 27.03)	nan (nan, nan, nan, nan)
MED	5.33 (-2.66, 3.08, 8.50, 12.40)	nan (nan, nan, nan, nan)	nan (nan, nan, nan, nan)
NAS	38.63 (28.21, 35.68, 38.61, 52.03)	77.04 (14.23, 23.80, 95.15, 175.00)	nan (nan, nan, nan, nan)
NEU	25.73 (11.16, 15.54, 27.37, 48.84)	28.98 (-0.06, 20.55, 23.45, 71.99)	nan (nan, nan, nan, nan)
TIB	1.51 (-4.43, -2.15, 5.48, 7.15)	-0.91 (-5.86, -1.35, -1.01, 4.57)	-0.62 (-3.98, -0.39, 0.09, 1.80)
WAS	2.20 (-3.50, -2.15, 5.66, 8.79)	8.91 (-3.63, -0.40, 11.07, 28.59)	55.47 (-7.84, -4.22, 26.55, 207.38)
WNA	-5.51 (-13.92, -12.35, -1.90, 6.12)	-27.68 (-55.40, -52.71, -11.54, 8.93)	nan (nan, nan, nan, nan)
mid-lat	26.06 (15.24, 16.03, 36.15, 36.84)	52.88 (23.79, 33.17, 70.01, 84.56)	74.07 (-11.73, -7.24, 81.75, 233.51)

Region	7-day warm period	14-day warm period	21-day warm period
ALA	1.39 (-0.69, 0.95, 2.20, 3.10)	0.79 (-3.20, 0.49, 2.75, 3.13)	-1.02 (-5.67, -4.95, 1.97, 4.55)
CAS	0.92 (-0.24, 0.54, 1.20, 2.18)	2.01 (-1.53, -0.12, 3.80, 5.89)	2.55 (-4.54, 2.25, 5.38, 7.12)
CEU	1.29 (-0.65, -0.53, 1.62, 4.71)	4.82 (-1.42, 0.52, 9.63, 10.54)	5.67 (-5.06, -0.83, 13.49, 15.09)
CGI	-0.53 (-0.97, -0.74, -0.50, 0.10)	-0.36 (-2.27, -1.44, -1.10, 3.39)	0.51 (-3.19, -2.37, -1.42, 9.04)
CNA	1.32 (0.05, 1.45, 1.61, 2.14)	2.85 (0.50, 2.62, 4.11, 4.16)	1.89 (-1.48, 1.49, 2.62, 4.92)
EAS	1.92 (-1.52, 0.72, 2.04, 6.45)	2.42 (-3.71, 1.75, 2.37, 9.28)	2.67 (-5.65, 2.13, 3.70, 10.52)
ENA	1.96 (0.88, 1.97, 2.31, 2.66)	4.66 (4.09, 4.32, 5.00, 5.21)	5.30 (3.93, 5.39, 5.69, 6.17)
MED	0.44 (-1.13, -0.86, 1.16, 2.59)	0.73 (-2.54, -2.26, 2.90, 4.80)	0.03 (-4.57, -3.66, 3.51, 4.85)
NAS	3.78 (2.99, 3.52, 4.02, 4.59)	5.82 (3.34, 6.01, 6.92, 7.02)	7.04 (2.90, 7.09, 9.02, 9.16)
NEU	0.09 (-0.47, -0.45, 0.31, 0.99)	2.12 (-0.14, 1.91, 2.22, 4.50)	2.61 (0.54, 1.59, 3.87, 4.44)
TIB	1.93 (-1.41, 1.49, 2.30, 5.35)	3.09 (-6.05, 3.56, 6.89, 7.97)	3.04 (-15.49, 7.25, 7.75, 12.67)
WAS	0.87 (-0.75, 0.37, 0.77, 3.10)	0.15 (-2.45, -0.47, -0.32, 3.84)	-0.42 (-5.14, -0.43, -0.29, 4.20)
WNA	2.20 (1.76, 2.29, 2.36, 2.40)	4.02 (2.65, 2.72, 4.00, 6.70)	3.62 (-0.62, 0.57, 5.46, 9.07)
mid-lat	2.09 (1.11, 1.72, 2.13, 3.39)	3.96 (1.92, 3.74, 4.18, 6.02)	4.11 (-0.43, 4.35, 5.88, 6.65)

Region	7-day dry-warm period	14-day dry-warm period	21-day dry-warm period
ALA	-3.53 (-9.77, -4.47, -2.86, 3.00)	-9.24 (-19.43, -12.16, -5.21, -0.13)	-13.31 (-22.61, -18.65, -13.05, 1.05)
CAS	1.44 (0.64, 1.00, 1.27, 2.86)	2.98 (-0.33, 0.63, 5.54, 6.07)	2.95 (-1.80, 0.64, 5.40, 7.57)
CEU	5.71 (-0.73, 6.80, 7.05, 9.71)	7.49 (-5.43, 9.70, 12.31, 13.37)	11.32 (-0.65, 10.41, 11.37, 24.13)
CGI	0.57 (-0.80, -0.45, -0.15, 3.67)	1.07 (-2.93, -0.71, 0.23, 7.68)	1.63 (-4.06, -1.39, 1.76, 10.19)
CNA	8.34 (0.93, 3.28, 11.06, 18.09)	12.43 (-3.12, 1.89, 16.08, 34.87)	13.06 (-13.04, 4.16, 14.52, 46.62)
EAS	1.46 (-4.96, 0.12, 2.94, 7.73)	0.93 (-9.66, -1.33, 7.25, 7.46)	0.86 (-8.27, -3.94, 0.68, 14.98)
ENA	7.06 (2.63, 7.66, 8.19, 9.75)	20.85 (11.20, 13.41, 16.91, 41.90)	20.61 (7.80, 19.30, 22.98, 32.37)
MED	1.85 (-0.50, -0.40, 2.22, 6.08)	2.09 (-2.21, -1.59, 3.13, 9.03)	1.94 (-2.82, -2.66, 4.54, 8.70)
NAS	4.59 (2.32, 4.41, 4.63, 7.02)	5.74 (-0.13, 5.10, 8.85, 9.13)	3.46 (-4.29, -1.11, 5.67, 13.58)
NEU	3.72 (1.73, 3.66, 4.28, 5.19)	9.64 (3.01, 7.88, 13.20, 14.49)	9.76 (0.38, 6.14, 14.23, 18.30)
TIB	4.83 (2.58, 4.12, 4.59, 8.05)	7.16 (2.14, 6.07, 9.83, 10.61)	11.51 (-7.17, 13.17, 18.81, 21.21)
WAS	0.67 (-0.51, -0.38, 1.36, 2.22)	0.76 (-3.13, -0.06, 1.79, 4.45)	1.06 (-6.46, 0.24, 2.39, 8.09)
WNA	2.82 (0.69, 3.02, 3.18, 4.37)	2.30 (-0.73, 1.69, 2.40, 5.85)	0.76 (-2.30, -0.78, -0.01, 6.12)
mid-lat	3.57 (1.70, 4.09, 4.21, 4.27)	3.89 (0.54, 4.62, 4.81, 5.60)	2.56 (-2.05, 3.22, 3.87, 5.20)

##################

Region	7-day dry period	14-day dry period	21-day dry period
ALA	-4.24 (-9.05 to 1.38)	-5.52 (-13.18 to 3.24)	-7.90 (-17.57 to 3.24)
CAS	0.41 (-0.39 to 0.98)	0.39 (-1.27 to 1.46)	0.71 (-1.17 to 1.80)
CEU	4.59 (-0.72 to 10.34)	7.95 (-1.79 to 16.84)	10.18 (-5.77 to 21.06)
CGI	-3.94 (-5.19 to -2.76)	-6.71 (-9.44 to -3.49)	-9.09 (-13.39 to -3.94)
CNA	7.26 (-1.32 to 16.07)	13.43 (-0.99 to 36.75)	15.12 (0.83 to 45.69)
EAS	0.47 (-2.82 to 4.42)	-2.08 (-10.16 to 7.05)	-6.10 (-18.29 to 7.27)
ENA	4.30 (-0.28 to 6.53)	13.35 (7.97 to 17.77)	26.00 (21.07 to 30.64)
MED	3.36 (-0.05 to 9.78)	5.32 (-0.56 to 16.29)	6.70 (-1.21 to 20.89)
NAS	3.38 (0.78 to 5.52)	5.00 (0.16 to 8.66)	6.02 (0.91 to 10.51)
NEU	0.56 (-1.49 to 2.73)	2.81 (-0.07 to 5.09)	5.38 (1.89 to 8.18)
TIB	1.77 (0.07 to 2.91)	1.14 (-0.23 to 3.96)	0.72 (-2.41 to 4.41)
WAS	1.28 (0.77 to 2.08)	1.66 (-0.15 to 3.06)	1.86 (-0.56 to 4.32)
WNA	1.07 (-2.37 to 4.42)	0.84 (-2.69 to 5.95)	-0.74 (-7.41 to 5.48)
mid-lat	2.61 (1.11 to 4.21)	3.08 (-0.10 to 5.39)	2.74 (-1.17 to 5.73)

Region	7-day 5mm period	14-day 5mm period	21-day 5mm period
ALA	17.33 (7.70 to 32.12)	17.93 (-38.16 to 88.91)	128.64 (-25.29 to 282.58)
CAS	-7.43 (-16.62 to 4.32)	-12.22 (-26.29 to 21.17)	-20.28 (-42.57 to 2.01)
CEU	17.65 (-0.14 to 34.29)	43.76 (11.16 to 120.79)	nan (nan to nan)
CGI	17.37 (3.04 to 29.87)	58.62 (-26.15 to 92.06)	nan (nan to nan)
CNA	8.14 (-3.47 to 17.77)	-0.71 (-49.91 to 32.57)	nan (nan to nan)
EAS	13.34 (4.47 to 22.93)	16.79 (3.60 to 29.49)	18.93 (3.49 to 32.92)
ENA	11.28 (8.00 to 17.44)	8.64 (-15.08 to 27.03)	nan (nan to nan)
MED	5.33 (-2.66 to 12.40)	nan (nan to nan)	nan (nan to nan)
NAS	38.63 (28.21 to 52.03)	77.04 (14.23 to 175.00)	nan (nan to nan)
NEU	25.73 (11.16 to 48.84)	28.98 (-0.06 to 71.99)	nan (nan to nan)
TIB	1.51 (-4.43 to 7.15)	-0.91 (-5.86 to 4.57)	-0.62 (-3.98 to 1.80)
WAS	2.20 (-3.50 to 8.79)	8.91 (-3.63 to 28.59)	55.47 (-7.84 to 207.38)
WNA	-5.51 (-13.92 to 6.12)	-27.68 (-55.40 to 8.93)	nan (nan to nan)
mid-lat	26.06 (15.24 to 36.84)	52.88 (23.79 to 84.56)	74.07 (-11.73 to 233.51)

Region	7-day warm period	14-day warm period	21-day warm period
ALA	1.39 (-0.69 to 3.10)	0.79 (-3.20 to 3.13)	-1.02 (-5.67 to 4.55)
CAS	0.92 (-0.24 to 2.18)	2.01 (-1.53 to 5.89)	2.55 (-4.54 to 7.12)
CEU	1.29 (-0.65 to 4.71)	4.82 (-1.42 to 10.54)	5.67 (-5.06 to 15.09)
CGI	-0.53 (-0.97 to 0.10)	-0.36 (-2.27 to 3.39)	0.51 (-3.19 to 9.04)
CNA	1.32 (0.05 to 2.14)	2.85 (0.50 to 4.16)	1.89 (-1.48 to 4.92)
EAS	1.92 (-1.52 to 6.45)	2.42 (-3.71 to 9.28)	2.67 (-5.65 to 10.52)
ENA	1.96 (0.88 to 2.66)	4.66 (4.09 to 5.21)	5.30 (3.93 to 6.17)
MED	0.44 (-1.13 to 2.59)	0.73 (-2.54 to 4.80)	0.03 (-4.57 to 4.85)
NAS	3.78 (2.99 to 4.59)	5.82 (3.34 to 7.02)	7.04 (2.90 to 9.16)
NEU	0.09 (-0.47 to 0.99)	2.12 (-0.14 to 4.50)	2.61 (0.54 to 4.44)
TIB	1.93 (-1.41 to 5.35)	3.09 (-6.05 to 7.97)	3.04 (-15.49 to 12.67)
WAS	0.87 (-0.75 to 3.10)	0.15 (-2.45 to 3.84)	-0.42 (-5.14 to 4.20)
WNA	2.20 (1.76 to 2.40)	4.02 (2.65 to 6.70)	3.62 (-0.62 to 9.07)
mid-lat	2.09 (1.11 to 3.39)	3.96 (1.92 to 6.02)	4.11 (-0.43 to 6.65)

Region	7-day dry-warm period	14-day dry-warm period	21-day dry-warm period
ALA	-3.53 (-9.77 to 3.00)	-9.24 (-19.43 to -0.13)	-13.31 (-22.61 to 1.05)
CAS	1.44 (0.64 to 2.86)	2.98 (-0.33 to 6.07)	2.95 (-1.80 to 7.57)
CEU	5.71 (-0.73 to 9.71)	7.49 (-5.43 to 13.37)	11.32 (-0.65 to 24.13)
CGI	0.57 (-0.80 to 3.67)	1.07 (-2.93 to 7.68)	1.63 (-4.06 to 10.19)
CNA	8.34 (0.93 to 18.09)	12.43 (-3.12 to 34.87)	13.06 (-13.04 to 46.62)
EAS	1.46 (-4.96 to 7.73)	0.93 (-9.66 to 7.46)	0.86 (-8.27 to 14.98)
ENA	7.06 (2.63 to 9.75)	20.85 (11.20 to 41.90)	20.61 (7.80 to 32.37)
MED	1.85 (-0.50 to 6.08)	2.09 (-2.21 to 9.03)	1.94 (-2.82 to 8.70)
NAS	4.59 (2.32 to 7.02)	5.74 (-0.13 to 9.13)	3.46 (-4.29 to 13.58)
NEU	3.72 (1.73 to 5.19)	9.64 (3.01 to 14.49)	9.76 (0.38 to 18.30)
TIB	4.83 (2.58 to 8.05)	7.16 (2.14 to 10.61)	11.51 (-7.17 to 21.21)
WAS	0.67 (-0.51 to 2.22)	0.76 (-3.13 to 4.45)	1.06 (-6.46 to 8.09)
WNA	2.82 (0.69 to 4.37)	2.30 (-0.73 to 5.85)	0.76 (-2.30 to 6.12)
mid-lat	3.57 (1.70 to 4.27)	3.89 (0.54 to 5.60)	2.56 (-2.05 to 5.20)




'''






#
