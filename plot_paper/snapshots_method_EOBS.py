import os,sys,glob,time,collections,signal,gc,pickle
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
mpl.use('Agg')

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

data_path='data/EOBS/All-Hist/'

events = {
	# 'russianHW2010':{'lon':37.25, 'lat':55.25, 'year':2010, 'name':'Moscow 2010'},
	'BerlinHW2018':{'lon':13.25, 'lat':53.25, 'years':[2018.24,2018.75], 'name':'Berlin 2018'},
	# 'BerlinFL2017':{'lon':13.25, 'lat':53.25, 'years':[2017.24,2017.75], 'name':'Berlin 2017'},
	# # 'Berlin2017-2018':{'lon':13.25, 'lat':53.25, 'years':[2017,2018.8], 'name':'Berlin 2017-2018'},
	# 'balkanFL2014':{'lon':19.75, 'lat':44.25, 'years':[2014.24,2014.75],'name':'Valjevo 2014'},
	# 'Kragujevac2014':{'lon':20.75, 'lat':44.25, 'years':[2014.24,2014.75],'name':'Kragujevac 2014'},
	# 'Cacak2014':{'lon':20.25, 'lat':44.25, 'years':[2014.24,2014.75],'name':'Serbia 2014'},
	# 'euroFL2016':{'lon':9.25, 'lat':48.75, 'year':2016,'name':'Stuttgart 2016'},
	'ParisFL2016':{'lon':2.25, 'lat':48.75, 'years':[2016.24,2016.75],'name':'Paris 2016'},
	#'euroFL2010':{'lon':18.75, 'lat':49.25, 'year':2010, 'name': 'Ostrau 2010'},
	# 'euroHW2003':{'lon':2.75, 'lat':48.25, 'years':[2003.24,2003.75],'name': 'Paris 2003'},
	}

for event_name,event in events.items():

	lat_,lon_,year_ = event['lat'],event['lon'],min(event['years'])

	pkl_file=open('data/EOBS/snapshots/'+event_name+'.pkl', 'rb')
	data = pickle.load(pkl_file);	pkl_file.close()

	tas=data['tas']
	tas_anom=data['tas_anom']
	pr=data['pr']
	tas_time_axis=data['tas_time_axis']
	pr_time_axis=data['pr_time_axis']
	months=data['months']
	ticks=data['ticks']
	periods=data['periods']
	pr_time_id=data['pr_time_id']
	tas_time_id=data['tas_time_id']
	states=data['states']

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

	axes[0].set_ylabel('temp anom [K]')

	axes[1].plot(pr_time_axis[pr_time_id],pr.ix[pr_time_id],marker='.',color='gray',linestyle='-',linewidth=0.4)
	for tt,ttas,st in zip(pr_time_axis[pr_time_id],pr.ix[pr_time_id],states['5mm'].ix[pr_time_id]):
		if st:
			axes[1].plot(tt,ttas,'.c')
	# for tt,ttas,st in zip(pr_time_axis[pr_time_id],pr.ix[pr_time_id],states['10mm'].ix[pr_time_id]):
	# 	if st:
	# 		axes[1].plot(tt,ttas,'.b')
	for tt,ttas,st in zip(pr_time_axis[pr_time_id],pr.ix[pr_time_id],states['dry'].ix[pr_time_id]):
		if st:
			axes[1].plot(tt,ttas,'.',color='orange')

	axes[1].set_ylabel('precip [mm]')
	axes[1].set_yscale('log')
	axes[1].set_ylim(1,100)

	for ax in axes:
		ax.set_xlim(min(event['years']),max(event['years']))

	# axes[2].axis('off')
	# axes[2].set_title('periods')

	state_names = ['warm','dry','dry-warm','5mm']
	colors = ['#FF3030','#FF8C00','#BF3EFF','#009ACD']
	positions = [8,7,6,5,4]

	for state,color,pos in zip(state_names,colors,positions):
		mid=periods[state]['period_midpoints'].values
		nona = np.where(np.isfinite(mid))
		mid = np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in num2date(mid[nona], units = pr_time.units)])
		periods_ = np.where((mid>min(event['years'])) & (mid<=max(event['years'])))
		length=periods[state]['period_length'].ix[periods_] / 365.
		for ll,mm in zip(length,mid[periods_]):
			axes[2].fill_between([mm-np.abs(ll)/2.,mm+np.abs(ll)/2.],[pos-0.4,pos-0.4],[pos+0.4,pos+0.4],color=color,alpha=0.6,edgecolor='w',linewidth=0.0)



	axes[2].set_yticks(positions)
	axes[2].set_yticklabels(['warm','dry','dry-warm','rainy'])
	axes[2].set_xticks(ticks[:,2])
	axes[2].set_xticklabels([months[mn] for mn in ticks[:,1]])

	plt.suptitle(event['name']+' ('+str(lat_)+'N, '+str(lon_)+'E)')
	# plt.tight_layout()
	plt.savefig('plots/paper/snapshot_method_EOBS_'+event_name+'.png')
	plt.savefig('plots/paper/snapshot_method_EOBS_'+event_name+'.pdf')
