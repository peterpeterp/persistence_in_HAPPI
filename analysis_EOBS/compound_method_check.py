import os,sys,glob,time,collections,signal,gc
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import matplotlib.pyplot as plt
import seaborn as sns

os.chdir('/Users/peterpfleiderer/Projects/Persistence')

data_path='data/EOBS/All-Hist/'

lat_,lon_=55.25,37.25

nc_period=da.read_nc(data_path+'tg_0.50deg_reg_v17.0_period.nc')
tas_period={}
for name, value in nc_period.items():
	tas_period[name]=value[:,lat_,lon_]

nc_period=da.read_nc(data_path+'rr_0.50deg_reg_v17.0_period.nc')
pr_period={}
for name, value in nc_period.items():
	pr_period[name]=value[:,lat_,lon_]

nc_period=da.read_nc(data_path+'compound_period.nc4')
cpd_period={}
for name, value in nc_period.items():
	cpd_period[name]=value[:,lat_,lon_]

tas_anom=da.read_nc(data_path+'tg_0.50deg_reg_v17.0_anom.nc')['tas_anom'][:,lat_,lon_]
pr=da.read_nc(data_path+'rr_0.50deg_reg_v17.0_nofeb29.nc')['rr'][:,lat_,lon_]

tas_state=da.read_nc(data_path+'tg_0.50deg_reg_v17.0_state.nc')['state'][:,lat_,lon_]
pr_state=da.read_nc(data_path+'rr_0.50deg_reg_v17.0_state.nc')['state'][:,lat_,lon_]
cpd_state=da.read_nc(data_path+'compound_state.nc4')['state'][:,lat_,lon_]
gc.collect()

tas_time=nc_period['time']
datevar=num2date(tas_time,units = tas_time.units)
time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in datevar])

months={1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mai',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Okt',11:'Nov',12:'Dez'}
ticks=np.array([(dd.year,dd.month,stamp) for dd,stamp,yearfrc in zip(datevar,tas_time,time_axis) if dd.day==15 and yearfrc>2010 and yearfrc<=2011])

time_id=np.where((time_axis>2010) & (time_axis<=2011))[0]
time_stamps=tas_time[time_id].values




plt.close()
fig,axes = plt.subplots(nrows=3,ncols=1,gridspec_kw = {'height_ratios':[1,2,4]})
for ax in axes:
	ax.set_xlim(time_stamps[0],time_stamps[-1])
	ax.set_xticks([])

axes[0].axis('off')
axes[0].set_title('cold+wet - warm+dry')
periods_ = np.where((cpd_period['period_midpoints']>time_stamps[0]) & (cpd_period['period_midpoints']<=time_stamps[-1]))[0]
mid=cpd_period['period_midpoints'].ix[periods_]
length=cpd_period['period_length'].ix[periods_]
for ll,mm in zip(length,mid):
	axes[0].fill_between([mm-np.abs(ll)/2.-15,mm+np.abs(ll)/2.-15],[-1,-1],[1,1],color={-1:'darkcyan',1:'darkmagenta',0:'white'}[np.sign(ll)],alpha=0.3)

periods_ = np.where((pr_period['period_midpoints']>time_stamps[0]) & (pr_period['period_midpoints']<=time_stamps[-1]))[0]
mid=pr_period['period_midpoints'].ix[periods_]
length=pr_period['period_length'].ix[periods_]
for ll,mm in zip(length,mid):
	axes[1].fill_between([mm-np.abs(ll)/2.-15,mm+np.abs(ll)/2.-15],[7,7],[12,12],color={-1:'brown',1:'cyan'}[np.sign(ll)],alpha=0.3)
axes[1].plot(time_stamps,pr.ix[time_id],color='gray')
axes[1].set_title('dry - wet')
axes[1].set_ylabel('precip [mm]')

periods_ = np.where((tas_period['period_midpoints']>time_stamps[0]) & (tas_period['period_midpoints']<=time_stamps[-1]))[0]
mid=tas_period['period_midpoints'].ix[periods_]
length=tas_period['period_length'].ix[periods_]
for ll,mm in zip(length,mid):
	axes[2].fill_between([mm-np.abs(ll)/2.-15,mm+np.abs(ll)/2.-15],[-3,-3],[3,3],color={-1:'blue',1:'red'}[np.sign(ll)],alpha=0.3)
axes[2].plot(time_stamps,tas_anom.ix[time_id],color='gray')
axes[2].set_xticks(ticks[:,2])
axes[2].set_xticklabels([months[mn] for mn in ticks[:,1]])
axes[2].set_title('cold - warm')
axes[2].set_ylabel('temp anom [K]')

plt.suptitle('Moscow 2010')
# plt.tight_layout()
plt.savefig('plots/EOBS_compound_moscow_2010.png')
