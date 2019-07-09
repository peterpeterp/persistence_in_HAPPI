import os,sys,glob,time,collections,signal,gc,pickle
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('classic')

from matplotlib import rc
rc('text', usetex=True)

from matplotlib import rcParams
rcParams['font.family'] = 'Arial'

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

data_path='data/EOBS/All-Hist/'

events = {
	# 'russianHW2010':{'lon':37.25, 'lat':55.25, 'year':2010, 'name':'Moscow 2010'},
	'BerlinHW2018':{'lon':13.25, 'lat':53.25, 'years':[2018.24,2018.75], 'name':'Berlin 2018', 'labels':['a','b','c']},
	# 'BerlinFL2017':{'lon':13.25, 'lat':53.25, 'years':[2017.24,2017.75], 'name':'Berlin 2017'},
	# # 'Berlin2017-2018':{'lon':13.25, 'lat':53.25, 'years':[2017,2018.8], 'name':'Berlin 2017-2018'},
	# 'balkanFL2014':{'lon':19.75, 'lat':44.25, 'years':[2014.24,2014.75],'name':'Valjevo 2014'},
	# 'Kragujevac2014':{'lon':20.75, 'lat':44.25, 'years':[2014.24,2014.75],'name':'Kragujevac 2014'},
	# 'Cacak2014':{'lon':20.25, 'lat':44.25, 'years':[2014.24,2014.75],'name':'Serbia 2014'},
	# 'euroFL2016':{'lon':9.25, 'lat':48.75, 'year':2016,'name':'Stuttgart 2016'},
	'ParisFL2016':{'lon':2.25, 'lat':48.75, 'years':[2016.24,2016.75],'name':'Paris 2016', 'labels':['d','e','f'], 'bar':[152./365.]},
	#'euroFL2010':{'lon':18.75, 'lat':49.25, 'year':2010, 'name': 'Ostrau 2010'},
	# 'euroHW2003':{'lon':2.75, 'lat':48.25, 'years':[2003.24,2003.75],'name': 'Paris 2003'},
	}

for event_name,event in events.items():

	lat_,lon_,year_ = event['lat'],event['lon'],int(min(event['years']))

	pkl_file=open('data/EOBS/snapshots/'+event_name+'.pkl', 'rb')
	data = pickle.load(pkl_file);	pkl_file.close()

	tas=data['tas']
	tas_anom=data['tas_anom']
	pr=data['pr']
	tas_time_axis=data['tas_time_axis']
	pr_time_axis=data['pr_time_axis']
	months={1: 'Jan',2: 'Feb',3: 'Mar',4: 'Apr',5: 'May',6: 'Jun',7: 'Jul',8: 'Aug',9: 'Sep',10: 'Okt',11: 'Nov',12: 'Dez'}
	ticks=data['ticks']
	periods=data['periods']
	pr_time_id=data['pr_time_id']
	tas_time_id=data['tas_time_id']
	states=data['states']
	pr_time=data['pr_time']
	thresholds=data['thresholds']


	plt.close()
	fig,axes = plt.subplots(nrows=3,ncols=1,gridspec_kw = {'height_ratios':[2,2,3]})
	for ax in axes:
		#ax.set_xlim(time_stamps[0],time_stamps[-1])
		ax.set_xticks([])

	axes[0].plot(tas_time_axis[tas_time_id],tas.ix[tas_time_id],marker='.',color='#C1CDCD',linestyle='-',linewidth=0.4)

	axes[0].plot(tas_time_axis[tas_time_id],tas_anom.ix[tas_time_id],marker='.',color='gray',linestyle='-',linewidth=0.4)
	for tt,ttas,st in zip(tas_time_axis[tas_time_id],tas_anom.ix[tas_time_id],states['warm'].ix[tas_time_id]):
		if st:
			axes[0].plot(tt,ttas,'.r')

	axes[0].plot([tas_time_axis[tas_time_id][0],year_+152./365.],[thresholds['MAM']]*2,'k-',zorder=0)
	axes[0].plot([year_+152./365.,year_+244./365.],[thresholds['JJA']]*2,'k-',zorder=0)
	axes[0].plot([year_+244./365.,tas_time_axis[tas_time_id][-1]],[thresholds['SON']]*2,'k-',zorder=0)
	axes[0].set_ylabel('Temperature\nanomaly [K]')

	axes[1].plot(pr_time_axis[pr_time_id],pr.ix[pr_time_id],marker='.',color='gray',linestyle='',linewidth=0.4)
	for tt,ttas,st in zip(pr_time_axis[pr_time_id],pr.ix[pr_time_id],states['5mm'].ix[pr_time_id]):
		if st:
			axes[1].plot(tt,ttas,'.c')
	# for tt,ttas,st in zip(pr_time_axis[pr_time_id],pr.ix[pr_time_id],states['10mm'].ix[pr_time_id]):
	# 	if st:
	# 		axes[1].plot(tt,ttas,'.b')
	for tt,ttas,st in zip(pr_time_axis[pr_time_id],pr.ix[pr_time_id],states['dry'].ix[pr_time_id]):
		if st:
			axes[1].plot(tt,ttas,'.',color='orange')

	axes[1].set_ylabel('Precipitation\n[mm]')
	axes[1].set_yscale('log')
	axes[1].axhline(1,linestyle='-',color='k',zorder=0)
	axes[1].axhline(5,linestyle='-',color='k',zorder=0)
	axes[1].set_ylim(0.1,100)
	axes[1].set_yticks([0.1,1,10,100])

	for ax in axes:
		ax.set_xlim(min(event['years']),max(event['years']))
		ax.yaxis.tick_right()
		ax.yaxis.set_label_position("right")
		ax.grid(False)

	# axes[2].axis('off')
	# axes[2].set_title('periods')

	state_names = ['warm','dry','dry-warm','5mm']
	colors = ['#FF3030','#FF8C00','#BF3EFF','#009ACD']
	positions = [8,7,6,5,4]

	for state,color,pos in zip(state_names,colors,positions):
		print('****** '+state)
		mid=periods[state]['period_midpoints'].values
		nona = np.where(np.isfinite(mid))
		mid = np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in num2date(mid[nona], units = pr_time.units)])
		periods_ = np.where((mid>min(event['years'])) & (mid<=max(event['years'])))
		length=periods[state]['period_length'].ix[periods_] / 365.
		for ll,mm in zip(length,mid[periods_]):
			axes[2].fill_between([mm-np.abs(ll)/2.,mm+np.abs(ll)/2.],[pos-0.4,pos-0.4],[pos+0.4,pos+0.4],color=color,alpha=0.6,edgecolor='w',linewidth=0.0)
			if ll*365>=7:
				print(ll*365,mm)


	axes[2].set_yticks(positions)
	axes[2].set_yticklabels(['warm','dry','dry-warm','rain'])
	axes[2].set_xticks(ticks[:,2]-15/365.)
	axes[2].set_xticklabels([months[mn] for mn in ticks[:,1]])

	if 'bar' in event.keys():
		for ax in axes:
			ax.axvline(x=2016+154./365.,ymin=-1.2,ymax=1,c="blue",linewidth=1,zorder=0, clip_on=False)
		ax.annotate('Seine\nflooding',xy=(2016+154./365.,3.2),color='blue', annotation_clip=False, fontsize=9, rotation=90, ha='left', va='center')

	for ax,lab in zip(axes,event['labels']):
		ax.annotate(lab, xy=(0.00, 0.95), xycoords='axes fraction', color='black', weight='bold', fontsize=12, horizontalalignment='left', backgroundcolor='w')

	plt.suptitle(event['name']+' ('+str(lat_)+'N, '+str(lon_)+'E)')
	plt.tight_layout(rect=[0, 0.03, 1, 0.95])
	plt.savefig('plots/final/snapshot_method_EOBS_'+event_name+'.pdf')
