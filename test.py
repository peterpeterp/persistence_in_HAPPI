import time,os,signal
import subprocess as sub
from scipy import stats
import dimarray as da
import numpy as np
import matplotlib.pylab as plt

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


def try_several_times(command,trials,seconds):
	for trial in range(trials):
		proc=sub.Popen(command,stdout=sub.PIPE,
                       shell=True, preexec_fn=os.setsid)
		print(os.getpgid(proc.pid))
		result=wait_timeout(proc,seconds)
		if result!='failed':
			break
	return(result)



data=da.read_nc('tas_Aday_CAM4-2degree_Plus20-Future_CMIP5-MMM-est1_v2-0_ens0098_period.nc')
eke=data['period_eke']
pers=data['period_length']
time=data['period_midpoints']

cor={}
for stat in ['pearson','pearson_sig','slope','intercept','r_value','p_value','std_err']:
	cor[stat]=da.DimArray(axes=[range(4),[-1,1],data.lat,data.lon],dims=['season','state','lat','lon'])
for y in data.lat:
	print(y)
	for x in data.lon:
		period_state=data['period_state'][:,y,x]
		if np.sum(np.abs(period_state))!=0:
			for state in [-1,1]:
				for season in range(4):
					select=(period_state==state) & (data['period_season'][:,y,x]==season)
					pers=data['period_length'][select,y,x]
					eke=data['period_eke'][select,y,x]
					time=data['period_midpoints'][select,y,x]

					slope, intercept, r_value, p_value, std_err = stats.linregress(time,pers)
					tmp_pers=pers-(intercept+slope*time)+pers.mean()

					slope, intercept, r_value, p_value, std_err = stats.linregress(time,eke)
					tmp_eke=eke-(intercept+slope*time)+eke.mean()

					pearson,pearson_sig=stats.pearsonr(pers,eke)
					slope,intercept,r_value,p_value,std_err = stats.linregress(eke,pers)

					for stat_name,stat in zip(['pearson','pearson_sig','slope','intercept','r_value','p_value','std_err'],[pearson,pearson_sig,slope,intercept,r_value,p_value,std_err]):
						cor[stat_name][season,state,y,x]=stat

ds=da.Dataset(cor)
ds.write_nc('cor_test.nc')
