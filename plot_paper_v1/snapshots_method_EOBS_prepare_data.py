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
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
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
	# 'OrleansFL2016':{'lon':1.75, 'lat':47.75, 'years':[2016.24,2016.75],'name':u'Orleans 2016'},
	#'euroFL2010':{'lon':18.75, 'lat':49.25, 'year':2010, 'name': 'Ostrau 2010'},
	# 'euroHW2003':{'lon':2.75, 'lat':48.25, 'years':[2003.24,2003.75],'name': 'Paris 2003'},
	}

for event_name,event in events.items():

	lat_,lon_,year_ = event['lat'],event['lon'],min(event['years'])
	if os.path.isdir(data_path+event_name) == False:
		os.system('mkdir '+data_path+event_name)
		for filename in glob.glob(data_path+'*merged*.nc'):
			os.system('cdo -O -sellonlatbox,'+','.join([str(i) for i in [lon_,lon_+0.5,lat_,lat_+0.5]]) + ' '+filename+' '+filename.replace('All-Hist/','All-Hist/'+event_name+'/'))

	periods={}
	nc_period=da.read_nc(data_path+event_name+'/'+'tg_0.50deg_reg_merged_period_warm.nc')
	periods['warm']={}
	for name, value in nc_period.items():
		periods['warm'][name]=value[:,lat_,lon_]

	nc_period=da.read_nc(data_path+event_name+'/'+'rr_0.50deg_reg_merged_period_dry.nc')
	periods['dry']={}
	for name, value in nc_period.items():
		periods['dry'][name]=value[:,lat_,lon_]

	nc_period=da.read_nc(data_path+event_name+'/'+'rr_0.50deg_reg_merged_period_5mm.nc')
	periods['5mm']={}
	for name, value in nc_period.items():
		periods['5mm'][name]=value[:,lat_,lon_]
	#
	# nc_period=da.read_nc(data_path+event_name+'/'+'rr_0.50deg_reg_merged_period_10mm.nc')
	# periods['10mm']={}
	# for name, value in nc_period.items():
	# 	periods['10mm'][name]=value[:,lat_,lon_]

	nc_period=da.read_nc(data_path+event_name+'/'+'cpd_0.50deg_reg_merged_period_dry-warm.nc')
	periods['dry-warm']={}
	for name, value in nc_period.items():
		periods['dry-warm'][name]=value[:,lat_,lon_]

	states={}
	states['warm']=da.read_nc(data_path+event_name+'/'+'tg_0.50deg_reg_merged_state.nc')['warm'][:,lat_,lon_]
	states['cold']=da.read_nc(data_path+event_name+'/'+'tg_0.50deg_reg_merged_state.nc')['cold'][:,lat_,lon_]
	states['dry']=da.read_nc(data_path+event_name+'/'+'rr_0.50deg_reg_merged_state.nc')['dry'][:,lat_,lon_]
	states['5mm']=da.read_nc(data_path+event_name+'/'+'rr_0.50deg_reg_merged_state.nc')['5mm'][:,lat_,lon_]
	states['10mm']=da.read_nc(data_path+event_name+'/'+'rr_0.50deg_reg_merged_state.nc')['10mm'][:,lat_,lon_]
	states['dry-warm']=da.read_nc(data_path+event_name+'/'+'cpd_0.50deg_reg_merged_state.nc')['dry-warm'][:,lat_,lon_]

	thresholds = {}
	nc_ = da.read_nc(data_path+'/'+'tg_0.50deg_reg_merged_state.nc')
	for season in ['MAM','JJA','SON','DJF']:
		thresholds[season] = nc_['threshold_'+season][lat_,lon_]
	gc.collect()


	nc_tas=da.read_nc(data_path+event_name+'/'+'tg_0.50deg_reg_merged.nc')
	tas=nc_tas['tg'][:,lat_,lon_]

	nc_tas_anom=da.read_nc(data_path+event_name+'/'+'tg_0.50deg_reg_merged_anom.nc')
	tas_anom=nc_tas_anom['tg'][:,lat_,lon_]

	nc_pr=da.read_nc(data_path+event_name+'/'+'rr_0.50deg_reg_merged.nc')
	pr=nc_pr['rr'][:,lat_,lon_]

	tas_time=nc_tas['time']
	datevar=num2date(tas_time, units = tas_time.units)
	tas_time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in datevar])
	#tas_time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in datevar])

	pr_time=nc_pr['time']
	datevar=num2date(pr_time, units = pr_time.units)
	pr_time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in datevar])

	months={1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mai',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Okt',11:'Nov',12:'Dez'}
	ticks=np.array([(dd.year,dd.month,yearfrc) for dd,yearfrc in zip(datevar,pr_time_axis) if dd.day == 15 and yearfrc>min(event['years']) and yearfrc<=max(event['years'])])

	pr_time_id=np.where((pr_time_axis>min(event['years'])) & (pr_time_axis<=max(event['years'])))[0]
	tas_time_id=np.where((tas_time_axis>min(event['years'])) & (tas_time_axis<=max(event['years'])))[0]


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

	out = {'tas':tas, 'tas_anom':tas_anom, 'pr':pr, 'tas_time_axis': tas_time_axis, 'pr_time_axis':pr_time_axis, 'months':months, 'ticks':ticks, 'periods':periods, 'pr_time_id':pr_time_id, 'tas_time_id':tas_time_id, 'states':states, 'pr_time':pr_time, 'tas_time':tas_time, 'thresholds':thresholds}

	output = open('data/EOBS/snapshots/'+event_name+'.pkl', 'wb')
	pickle.dump(out, output); output.close()
