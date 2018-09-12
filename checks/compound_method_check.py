import os,sys,glob,time,collections,signal,gc,argparse
import numpy as np
from netCDF4 import Dataset,num2date
import random as random
import dimarray as da
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append('/global/homes/p/pepflei/persistence_in_models/')
import __settings
model_dict=__settings.model_dict

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
from persistence_functions import *

parser = argparse.ArgumentParser(description=' ',epilog=' ')
parser.add_argument('--model','-m', default='CAM4-2degree')
parser.add_argument('--run','-r', default='ens0000')
parser.add_argument('--scenario','-s', default='All-Hist')
parser.add_argument('--year','-y', default=2010)
parser.add_argument('--lat_','-y', default=54.)
parser.add_argument('--lon_','-x', default=37.5)

# Parse and evaluate
args = parser.parse_args()
args.func(args)

model=args.model
run=args.run
scenario=args.scenario
year=args.year
lat_=args.lat_
lon_=args.lon_

in_path=model_dict[model]['in_path']
grid=model_dict[model]['grid']

try:
	os.chdir('/global/homes/p/pepflei/')
	working_path='/global/cscratch1/sd/pepflei/'+model+'/'
	land_mask_file='/global/homes/p/pepflei/masks/landmask_'+grid+'_NA-1.nc'
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
	working_path='data/'+model+'/'
	land_mask_file='data/'+model+'/landmask_'+grid+'_NA-1.nc'



nc_period=da.read_nc(working_path+'/'+scenario+'/'+'tas_Aday_'+model+'_'+scenario+'_est1_v1-0_'+run+'_period.nc')
tas_period={}
for name, value in nc_period.items():
	tas_period[name]=value[:,lat_,lon_]

nc_period=da.read_nc(working_path+'/'+scenario+'/'+'pr_Aday_'+model+'_'+scenario+'_est1_v1-0_'+run+'_period.nc')
pr_period={}
for name, value in nc_period.items():
	pr_period[name]=value[:,lat_,lon_]

nc_period=da.read_nc(working_path+'/'+scenario+'/'+'compound_Aday_'+model+'_'+scenario+'_est1_v1-0_'+run+'_period.nc')
compound_period={}
for name, value in nc_period.items():
	compound_period[name]=value[:,lat_,lon_]

nc_state=da.read_nc(working_path+'/'+scenario+'/'+'tas_Aday_'+model+'_'+scenario+'_est1_v1-0_'+run+'_anom.nc')
tas_anom=nc_state['tas'].squeeze()[:,lat_,lon_]

nc_state=da.read_nc(working_path+'/'+scenario+'/'+'pr_Aday_'+model+'_'+scenario+'_est1_v1-0_'+run+'.nc')
pr=nc_state['pr'].squeeze()[:,lat_,lon_]*86400


tas_state=da.read_nc(working_path+'/'+scenario+'/'+'tas_Aday_'+model+'_'+scenario+'_est1_v1-0_'+run+'_state.nc')['state'][:,lat_,lon_]
pr_state=da.read_nc(working_path+'/'+scenario+'/'+'pr_Aday_'+model+'_'+scenario+'_est1_v1-0_'+run+'_state.nc')['state'][:,lat_,lon_]
compound_state=da.read_nc(working_path+'/'+scenario+'/'+'compound_Aday_'+model+'_'+scenario+'_est1_v1-0_'+run+'_state.nc')['state'][:,lat_,lon_]

gc.collect()

tas_time=nc_state['time'].values
datevar=num2date(tas_time,units = nc_state['time'].units)
time_axis=np.array([dd.year + (dd.timetuple().tm_yday-1) / 365. for dd in datevar])

months={1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mai',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Okt',11:'Nov',12:'Dez'}

time_id=np.where((time_axis>year) & (time_axis<=year+1))[0]
time_stamps=tas_time[time_id]

# plot
plt.close()
fig,axes = plt.subplots(nrows=3,ncols=1,gridspec_kw = {'height_ratios':[1,2,4]})
for ax in axes:
	ax.set_xlim(time_stamps[0],time_stamps[-1])
	ax.set_xticks([])

axes[0].axis('off')
axes[0].set_title('cold+wet - warm+dry')
periods_ = np.where((compound_period['period_midpoints']>time_stamps[0]) & (compound_period['period_midpoints']<=time_stamps[-1]))[0]
mid=compound_period['period_midpoints'].ix[periods_]
length=compound_period['period_length'].ix[periods_]
for ll,mm in zip(length,mid):
	axes[0].fill_between([mm-np.abs(ll)/2.,mm+np.abs(ll)/2.],[-1,-1],[1,1],color={-1:'darkcyan',1:'darkmagenta',0:'white'}[np.sign(ll)],alpha=0.3)

periods_ = np.where((pr_period['period_midpoints']>time_stamps[0]) & (pr_period['period_midpoints']<=time_stamps[-1]))[0]
mid=pr_period['period_midpoints'].ix[periods_]
length=pr_period['period_length'].ix[periods_]
for ll,mm in zip(length,mid):
	axes[1].fill_between([mm-np.abs(ll)/2.,mm+np.abs(ll)/2.],[7,7],[12,12],color={-1:'brown',1:'cyan'}[np.sign(ll)],alpha=0.3)
axes[1].plot(time_stamps,pr[time_stamps],color='gray')
axes[1].set_title('dry - wet')
axes[1].set_ylabel('precip [mm]')

periods_ = np.where((tas_period['period_midpoints']>time_stamps[0]) & (tas_period['period_midpoints']<=time_stamps[-1]))[0]
mid=tas_period['period_midpoints'].ix[periods_]
length=tas_period['period_length'].ix[periods_]
for ll,mm in zip(length,mid):
	axes[2].fill_between([mm-np.abs(ll)/2.,mm+np.abs(ll)/2.],[-3,-3],[3,3],color={-1:'blue',1:'red'}[np.sign(ll)],alpha=0.3)
axes[2].plot(time_stamps,tas_anom[time_stamps],color='gray')
# axes[2].set_xticks(ticks[:,2])
# axes[2].set_xticklabels([months[mn] for mn in ticks[:,1]])
axes[2].set_title('cold - warm')
axes[2].set_ylabel('temp anom [K]')

plt.suptitle(' '.join([str(xx) for xx in [model,scenario,run,lat_,lon_,year]]))
# plt.tight_layout()
plt.savefig('plots/checks/'+'_'.join([str(xx) for xx in [model,scenario,run,lat_,lon_,year]])+'.png')
