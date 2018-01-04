import os,sys,glob,time,collections,gc,itertools,timeit
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Documents/Projects/Persistence/weather_persistence/')
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
    os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
    working_path='data/'+model+'/'

for scenario in ['All-Hist','Plus20-Future','Plus15-Future']:
    run_count=0
    all_files=glob.glob(working_path+scenario+'/*_period*')
    for in_file in all_files:
        out_file=in_file.replace('_period','_summer')
        if overwrite and os.path.isfile(out_file):  os.system('rm '+out_file)
        if os.path.isfile(out_file)==False:
            print in_file
            #state_check=da.read_nc(in_file.replace('_period','_state'))['state']
            #tas=da.read_nc(in_file.replace('_period',''))['tas'][state_check.time,:,:]
            tas=da.read_nc(in_file.replace('_period',''))['tas'].ix[45:-45,::]
            tt=np.asarray(tas.squeeze(),np.float)
            datevar = num2date(tas.time,units = "days since 1979-01-01 00:00:00",calendar = "proleptic_gregorian")
            year=np.array([int(str(date).split("-")[0])	for date in datevar[:]],np.int32)


            period=da.read_nc(in_file)
            mm=np.asarray(period['period_midpoints']-tas.time[0],np.int32)
            ll=np.asarray(period['period_length'],np.int32)
            seas=np.asarray(period['period_season'],np.int32)
            state=np.asarray(period['period_state'],np.int32)

            x90_thresh=np.asarray(da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc')['SummaryMeanQu'][scenario,'JJA','warm','qu_90'],np.float)

            time0=time.time()
            x90_hottest_day,x90_cum_temp,x90_mean_temp,x90_hottest_day_shift,TXx_in_x90,original_period_id=summer_period_analysis(ll,mm,seas,state,tt,x90_thresh,year,len(period.lat),len(period.lon),len(period.period_id))
            print time.time()-time0

            for tmp in [x90_hottest_day,x90_cum_temp,x90_mean_temp]:
                tmp[tmp==-99]=np.nan

            n_ID=x90_hottest_day.shape[0]
            ds=da.Dataset({
                'x90_hottest_day':da.DimArray(x90_hottest_day,axes=[range(n_ID),tas.lat,tas.lon],dims=['ID','lat','lon']),
                'x90_cum_temp':da.DimArray(x90_cum_temp,axes=[range(n_ID),tas.lat,tas.lon],dims=['ID','lat','lon']),
                'x90_mean_temp':da.DimArray(x90_mean_temp,axes=[range(n_ID),tas.lat,tas.lon],dims=['ID','lat','lon']),
                'x90_hottest_day_shift':da.DimArray(x90_hottest_day_shift,axes=[range(n_ID),tas.lat,tas.lon],dims=['ID','lat','lon']),
                'original_period_id':da.DimArray(original_period_id,axes=[range(n_ID),tas.lat,tas.lon],dims=['ID','lat','lon']),
                'TXx_in_x90':da.DimArray(TXx_in_x90[0:len(set(year)),:,:],axes=[sorted(set(year)),tas.lat,tas.lon],dims=['year','lat','lon']),
            })
            ds.write_nc(out_file,mode='w')

            print time.time()-time0


            # # check plot
            # plt.close()
            # year_uq=sorted(set(year))
            # day_in_year=[]
            # for yr in year_uq:
            #     day_in_year+=range(year[year==yr].shape[0])
            # day_in_year=np.array(day_in_year)
            # fig,axes= plt.subplots(nrows=2,ncols=5,figsize=(20,10))
            # for ax,yr in zip(axes.flatten(),year_uq):
            #     state_check_=state_check.values.squeeze()
            #     colors=np.array(day_in_year[year==yr],'str')
            #     colors[state_check_[year==yr,70,10]==-1]='b'
            #     colors[state_check_[year==yr,70,10]==1]='r'
            #     ax.scatter(day_in_year[year==yr],tas[:,tas.lat[70],tas.lon[10]].values[year==yr],color=colors)
            #     ids=original_period_id[:,70,10]
            #     ids=ids[0:np.argmax(ids)+1]
            #     xx=year[mm[ids,70,10]]
            #     ids=ids[year[mm[ids,70,10]]==yr]
            #     for id_ in ids:
            #         hl=int(abs(ll[id_,70,10])/2.)
            #         shift=hl%2
            #         days=np.arange(mm[id_,70,10]-hl+shift,mm[id_,70,10]+hl+shift)
            #         ax.plot(day_in_year[days],tt[days,70,10])
            #         print tt[days,70,10],np.max(tt[days,70,10]),x90_hottest_day[np.where(original_period_id[:,70,10]==id_)[0],70,10]
            #         ax.scatter([day_in_year[mm[id_,70,10]]],[x90_hottest_day[np.where(original_period_id[:,70,10]==id_)[0],70,10]],color='g')
            # plt.savefig('test.png',dpi=300)
            # asdas
