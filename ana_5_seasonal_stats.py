import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

model_dict={'MIROC':{'grid':'128x256','path':'/global/cscratch1/sd/pepflei/MIROC/MIROC5/'},
			'NorESM1':{'grid':'192x288','path':'/global/cscratch1/sd/pepflei/NCC/NorESM1-HAPPI/'},
			'ECHAM6-3-LR':{'grid':'96x192','path':'/global/cscratch1/sd/pepflei/MPI-M/ECHAM6-3-LR/'},
			'CAM4-2degree':{'grid':'96x144','path':'/global/cscratch1/sd/pepflei/ETH/CAM4-2degree/'},
}

model=sys.argv[1]
print model

#model='ECHAM6-3-LR'

overwrite=True

working_path=model_dict[model]['path']
grid=model_dict[model]['grid']

#working_path='data/tests/'



for scenario in ['Plus20-Future','Plus15-Future','All-Hist']:
# for scenario in ['']:
	all_files=glob.glob(working_path+scenario+'/*period*')

	# get time conversion
	tas=da.read_nc(all_files[0].replace('_period',''))
	time_axis=np.asarray(tas['time'])
	datevar = num2date(time_axis,units = "days since 1979-01-01 00:00:00",calendar = "proleptic_gregorian")
	year=np.array([int(str(date).split("-")[0])	for date in datevar[:]],np.int32)
	year_boundaries={yr:time_axis[year==yr][[0,-1]] for yr in set(year)}

	stat_Xpers_cum_heat=da.DimArray(axes=[range(100),sorted(set(year)),tas.lat,tas.lon],dims=['run','year','lat','lon'])
	stat_Xpers_hot_shift=da.DimArray(axes=[range(100),sorted(set(year)),tas.lat,tas.lon],dims=['run','year','lat','lon'])
	stat_Xpers_hot_temp=da.DimArray(axes=[range(100),sorted(set(year)),tas.lat,tas.lon],dims=['run','year','lat','lon'])
	stat_tasX_pers_rank=da.DimArray(axes=[range(100),sorted(set(year)),tas.lat,tas.lon],dims=['run','year','lat','lon'])

	for per_file,run in zip(all_files,range(len(all_files))):
		start_time=time.time()
		print per_file
		nc_in=Dataset(per_file,'r')
		per_len=nc_in.variables['period_length'][:,:,:]
		per_sea=nc_in.variables['period_season'][:,:,:]
		per_mid=nc_in.variables['period_midpoints'][:,:,:]
		per_id=range(per_mid.shape[0])
		nc_in.close()
		per_year=per_mid.copy()*np.nan
		for yr,bounds in year_boundaries.iteritems():
			per_year[np.where((per_mid>=bounds[0]) & (per_mid<=bounds[1]))]=yr

		nc_in=Dataset(per_file.replace('period','summer'),'r')
		hot_shift=nc_in.variables['hottest_day_shift'][:,:,:]
		hot_temp=nc_in.variables['hottest_day_temp'][:,:,:]
		cum_heat=nc_in.variables['cumulated_heat'][:,:,:]
		tasX=nc_in.variables['tasX'][:,:,:]
		summer_events=nc_in.variables['period_id'][:,:,:]
		nc_in.close()

		for x,lon in zip(range(len(tas.lon)),tas.lon):
			for y,lat in zip(range(len(tas.lat)),tas.lat):
				if np.sum(summer_events[:,y,x])!=0:
					tmp=summer_events[:,y,x]
					tmp=tmp[0:np.argmax(tmp)+1]
					for yr in year_boundaries.keys():
						summer_ids=np.where(per_year[tmp,y,x]==yr)[0]
						if len(summer_ids)!=0:
							event_ids=tmp[np.where(per_year[tmp,y,x]==yr)[0]]
							Xpers_id=np.argmax(per_len[event_ids,y,x])
							stat_Xpers_cum_heat[run,yr,lat,lon]=cum_heat[summer_ids[Xpers_id],y,x]
							stat_Xpers_hot_shift[run,yr,lat,lon]=hot_shift[summer_ids[Xpers_id],y,x]
							stat_Xpers_hot_temp [run,yr,lat,lon]=hot_temp[summer_ids[Xpers_id],y,x]
							if tasX[summer_ids[Xpers_id],y,x] in hot_temp[summer_ids,y,x]:
								stat_tasX_pers_rank[run,yr,lat,lon]=np.where(sorted(range(len(per_len[event_ids,y,x])),key=lambda i:per_len[event_ids,y,x][i])[::-1]==np.argmax(hot_temp[summer_ids,y,x]))[0]


		print time.time()-start_time

	out_file='data/'+model+'_'+scenario+'_SummerStats.nc'
	if overwrite and os.path.isfile(out_file): os.system('rm '+out_file)
	nc_out=Dataset(out_file,'w')
	nc_in=Dataset(all_files[0].replace('_period',''),'r')
	for dname, the_dim in nc_in.dimensions.iteritems():
	    if dname in ['lon','lat']:nc_out.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
	nc_out.createDimension('run', 100)
	nc_out.createDimension('year', len(sorted(set(year))))

	for v_name, varin in nc_in.variables.iteritems():
	    if v_name in ['lon','lat']:
	        outVar = nc_out.createVariable(v_name, varin.datatype, varin.dimensions)
	        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
	        outVar[:] = varin[:]

	outVar = nc_out.createVariable('year','i',('year',))
	outVar.long_name='year'
	outVar[:] = sorted(set(year))[:]

	outVar = nc_out.createVariable('stat_Xpers_cum_heat','f',('run','year','lat','lon',))
	outVar.long_name='sum over temperature of days in longest period'
	outVar[:] = np.asarray(stat_Xpers_cum_heat[:,:,:,:])

	outVar = nc_out.createVariable('stat_Xpers_hot_shift','f',('run','year','lat','lon',))
	outVar.long_name='shift between hottest day in period and middle of longest period'
	outVar[:] = np.asarray(stat_Xpers_hot_shift[:,:,:,:])

	outVar = nc_out.createVariable('stat_Xpers_hot_temp','f',('run','year','lat','lon',))
	outVar.long_name='temperature of hottest day in longest period'
	outVar[:] = np.asarray(stat_Xpers_hot_temp[:,:,:,:])

	outVar = nc_out.createVariable('stat_tasX_pers_rank','f',('run','year','lat','lon',))
	outVar.long_name='rank of the period in which the hottest day is found'
	outVar[:] = np.asarray(stat_tasX_pers_rank[:,:,:,:])

	nc_out.close()
	nc_in.close()
