import os,sys,glob,time,collections,gc,itertools,timeit,signal

import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
import random as random
import subprocess as sub

def wait_timeout(proc, seconds):
	"""Wait for a process to finish, or raise exception after timeout"""
	start = time.time()
	end = start + seconds
	interval = min(seconds / 1000.0, .25)

	while True:
		result = proc.poll()
		if result is not None:
			return result
		if time.time() >= end:
			os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
			return 'failed'
		time.sleep(interval)


def try_several_times(command,trials=2,seconds=60):
	for trial in range(trials):
		proc=sub.Popen(command,stdout=sub.PIPE,shell=True, preexec_fn=os.setsid)
		result=wait_timeout(proc,seconds)
		if result!='failed':
			break
	return(result)


sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Projects/Persistence/weather_persistence/')
from summer_persistence_analysis import *
from persistence_functions import *

try:
	model=sys.argv[1]
	print model
except:
	model='ECHAM6-3-LR'

overwrite=True

try:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
except:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
	working_path='data/'+model+'/'

sys.path.append('persistence_in_models/')
import __settings
model_dict=__settings.model_dict

in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

for scenario,selyears in zip(['Plus20-Future','Plus15-Future','All-Hist'],['2106/2115','2106/2115','2006/2015']):

	all_files=glob.glob(working_path+scenario+'/tas/tas_Aday_*_period*')
	if os.path.isdir(working_path+scenario+'/summerStat') == False:
		os.system('mkdir '+working_path+scenario+'/summerStat')
	if os.path.isdir(working_path+scenario+'/tas') == False:
		os.system('mkdir '+working_path+scenario+'/tas')

	print('finding periods\n10------50-------100')
	for in_file,progress in zip(all_files, np.array([['-']+['']*(len(all_files)/20+1)]*20).flatten()[0:len(all_files)]):
		sys.stdout.write(progress); sys.stdout.flush()
		run = in_file.split('_')[-2]
		out_file=in_file.replace('_period','_summer').replace('/tas/tas_Aday_','/summerStat/tas_Aday_')
		if overwrite and os.path.isfile(out_file):  os.system('rm '+out_file)
		if os.path.isfile(out_file)==False:

			raw_file=in_file.replace('_period','')
			if os.path.isfile(raw_file) == False:
				tmp_path=in_path+scenario+'/*/'+model_dict[model]['version'][scenario]+'/day/atmos/tas/'
				out_file_name_tmp=working_path+scenario+'/'+glob.glob(tmp_path+run+'/*')[0].split('/')[-1].split(run)[0]+run+'_tmp.nc'
				command='cdo -O mergetime '+tmp_path+run+'/* '+out_file_name_tmp
				result=try_several_times(command,2,60)
				result=try_several_times('cdo -O -selyear,'+selyears+' '+out_file_name_tmp+' '+raw_file,2,60)
				result=try_several_times('rm '+out_file_name_tmp)

			result=try_several_times('cdo -O yseasmean '+raw_file+' '+out_file.replace('_summer.nc','_seasMean.nc'),2,60)

			state_check=da.read_nc(in_file.replace('_period','_state'))['state']
			nc_tas=da.read_nc(raw_file)
			#print(raw_file)
			#print(nc_tas)
			tas=nc_tas['tas'][state_check.time,:,:]
			#tas=da.read_nc(raw_file)['tas'].ix[45:-45,::]
			tt=np.asarray(tas.squeeze(),np.float)
			datevar = num2date(tas.time,units = "days since 1979-01-01 00:00:00",calendar = "proleptic_gregorian")
			year=np.array([int(str(date).split("-")[0])	for date in datevar[:]],np.int32)

			lon=nc_tas['lon']; lon.units="degrees_east"
			lat=nc_tas['lat']; lat.units="degrees_north"

			period=da.read_nc(in_file)
			mm=np.asarray(period['period_midpoints']-tas.time[0],np.int32)
			ll=np.asarray(period['period_length'],np.int32)
			seas=np.asarray(period['period_season'],np.int32)
			state=np.asarray(period['period_state'],np.int32)

			#x90_thresh=np.asarray(da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc')['SummaryMeanQu'][scenario,'JJA','warm','qu_90'],np.float)

			result = {
				'length' : da.DimArray(['7','14','21','28'],axes=[['7','14','21','28']],dims=['length']),
				'lon': lon,
				'lat': lat,
				'hottest_day':da.DimArray(axes=[['7','14','21','28'],tas.lat,tas.lon],dims=['length','lat','lon']),
				'mean_temp':da.DimArray(axes=[['7','14','21','28'],tas.lat,tas.lon],dims=['length','lat','lon']),
				'hottest_day_shift':da.DimArray(axes=[['7','14','21','28'],tas.lat,tas.lon],dims=['length','lat','lon']),
				# 'original_period_id':da.DimArray(axes=[['7','14','21','28'],tas.lat,tas.lon],dims=['length','lat','lon']),
				#'TXx_in_x90':da.DimArray(TXx_in_x90[0:len(set(year)),:,:],axes=[['7','14','21','28'],sorted(set(year)),tas.lat,tas.lon],dims=['length_thresh','year','lat','lon']),
			}

			for per_len_thresh in [7,14,21,28][::-1]:
				thresh = mm.copy()[0,:,:] * 0.0 + float(per_len_thresh)
				hottest_day,x90_cum_temp,mean_temp,hottest_day_shift,TXx_in_x90,original_period_id,max_len=summer_period_analysis(ll,mm,seas,state,tt,thresh,year,len(period.lat),len(period.lon),len(period.period_id))

				for tmp,name in zip([hottest_day,mean_temp,hottest_day_shift],['hottest_day','mean_temp','hottest_day_shift']):
					tmp = np.array(tmp,np.float)
					tmp[tmp==-99] = np.nan
					result[name][str(per_len_thresh),:,:] = np.nanmean(tmp,axis=0)

			ds=da.Dataset(result)
			ds.write_nc(out_file,mode='w')






			# # check plot
			# import matplotlib.pyplot as plt
			# plt.close()
			# year_uq=sorted(set(year))
			# day_in_year=[]
			# for yr in year_uq:
			# 	day_in_year+=range(year[year==yr].shape[0])
			# day_in_year=np.array(day_in_year)
			# fig,axes= plt.subplots(nrows=2,ncols=5,figsize=(20,10))
			# for ax,yr in zip(axes.flatten(),year_uq):
			# 	state_check_=state_check.values.squeeze()
			# 	colors=np.array(day_in_year[year==yr],'str')
			# 	colors[state_check_[year==yr,70,10]==-1]='b'
			# 	colors[state_check_[year==yr,70,10]==1]='r'
			# 	ax.scatter(day_in_year[year==yr],tas[:,tas.lat[70],tas.lon[10]].values[year==yr],color=colors)
			# 	ids=original_period_id[:,70,10]
			# 	ids=ids[0:np.argmax(ids)+1]
			# 	xx=year[mm[ids,70,10]]
			# 	ids=ids[year[mm[ids,70,10]]==yr]
			# 	ax.set_title(ll[ids,70,10])
			# 	for id_ in ids:
			# 		l=int(abs(ll[id_,70,10])/2.)
			# 		h=int(round(abs(ll[id_,70,10])/2.))
			# 		shift=-(ll[id_,70,10]%2-1)
			# 		days=np.arange(mm[id_,70,10]-l+shift,mm[id_,70,10]+h+shift)
			# 		print(ll[id_,70,10],len(days),shift)
			# 		print(state_check_[days,70,10])
			# 		ax.plot(day_in_year[days],tt[days,70,10])
			# 		#print tt[days,70,10],np.max(tt[days,70,10]),x90_hottest_day[np.where(original_period_id[:,70,10]==id_)[0],70,10]
			# 		ax.scatter([day_in_year[mm[id_,70,10]]],[hottest_day[np.where(original_period_id[:,70,10]==id_)[0],70,10]],color='g')
			# plt.savefig('test.png',dpi=300)
#
