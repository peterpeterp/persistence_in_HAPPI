import os,sys,glob,time,collections,gc,pickle
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date


scenario='HadGHCND'
seasons=['MAM','JJA','DJF','SON','year']

pkl_file = open('data/'+scenario+'_counter.pkl', 'rb')
distr_dict = pickle.load(pkl_file)	;	pkl_file.close()  

nc_in=Dataset('data/HadGHCND_TMean_grided.1950-2014_state.nc','r')
#nc_in=Dataset('data/raw/tas_Aday_MIROC5_Plus15-Future_CMIP5-MMM-est1_v2-0_run001.nc','r')
lat=nc_in.variables['lat'][:]
lon=nc_in.variables['lon'][:]
nc_in.close()

out_dict={}
for season in seasons:
	out_dict[season]={}
	for state in [-1,1]:
		out_dict[season][state]={}
		for out in ['mean']+[1,5,10,25,50,75,90,95,99]:
			out_dict[season][state][out]=np.zeros([len(lat),len(lon)])

for iy in range(len(lat)):
	for ix in range(len(lon)):
		grid_cell=distr_dict[str(lat[iy])+'_'+str(lon[ix])]
		grid_cell['year']=grid_cell['MAM']+grid_cell['JJA']+grid_cell['SON']+grid_cell['DJF']

for season in seasons:
	print season
	for iy in range(len(lat)):
		start=time.time()
		print iy
		for ix in range(len(lon)):
			counter=distr_dict[str(lat[iy])+'_'+str(lon[ix])][season]
			tmp=[]
			lengths=counter.keys()
			if 0 in lengths: 
				lengths.remove(0)
			if len(lengths)>2:
				for key in lengths:
					for i in range(counter[key]):
						tmp.append(key)
				tmp=np.array(tmp)
				tmp_dict={-1:tmp[tmp<0],1:tmp[tmp>0]}
				for state in [-1,1]:
					out_dict[season][state]['mean'][iy,ix]=np.mean(state*tmp_dict[state])
					for qu in [1,5,10,25,50,75,90,95,99]:
						out_dict[season][state][qu][iy,ix]=np.percentile(state*tmp_dict[state],qu)

		print time.time()-start

out_dict['lon']=lon
out_dict['lat']=lat

output = open('data/'+scenario+'_summary.pkl', 'wb')
pickle.dump(out_dict, output)
output.close()


