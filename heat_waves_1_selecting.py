import os,sys,glob,time,collections,gc,itertools,timeit
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Documents/Projects/Persistence/weather_persistence/')
from persistence_functions import *

model=sys.argv[1]
print model

overwrite=True

model='ECHAM6-3-LR'

try:
    os.chdir('/global/homes/p/pepflei/HAPPI_persistence/')
    working_path='/global/cscratch1/sd/pepflei/'+model+'/'
except:
    os.chdir('/Users/peterpfleiderer/Documents/Projects/Persistence/')
    working_path='data/'+model+'/'

qu_90=da.read_nc('data/'+model+'/'+model+'_SummaryMeanQu.nc')['SummaryMeanQu'][:,'JJA','warm','qu_90']


for scenario in ['All-Hist','Plus20-Future','Plus15-Future']:
    run_count=0
    all_files=glob.glob(working_path+scenario+'/*_period*')
    print all_files
    for in_file in all_files:
        out_file=in_file.replace('_period','_summer_')
        claim_run_file=out_file.replace('.nc','_working_on')
        if os.path.isfile(claim_run_file)==False:
            claim_run=open(claim_run_file,'w')
            if overwrite and os.path.isfile(out_file):  os.system('rm '+out_file)
            if os.path.isfile(out_file)==False:
                print in_file
                tas=da.read_nc(in_file.replace('_period',''))['tas']
                datevar = num2date(tas.time,units = "days since 1979-01-01 00:00:00",calendar = "proleptic_gregorian")
                year=np.array([int(str(date).split("-")[0])	for date in datevar[:]],np.int32)
                year_uq=sorted(set(year))
                day_in_year=[]
                for yr in year_uq:
                    day_in_year+=range(year[year==yr].shape[0])
                day_in_year=np.array(day_in_year)

                    #state_check=da.read_nc(in_file.replace('_period','_state'))['state']

                period=da.read_nc(in_file)
                per_mid=period['period_midpoints']
                per_len=period['period_length']
                seas=period['period_season']
                state=period['period_state']

                x90_hottest_day=da.DimArray(axes=[range(150),per_len.lat,per_len.lon],dims=['ID','lat','lon'])
                x90_cum_temp=da.DimArray(axes=[range(150),per_len.lat,per_len.lon],dims=['ID','lat','lon'])
                x90_mean_temp=da.DimArray(axes=[range(150),per_len.lat,per_len.lon],dims=['ID','lat','lon'])
                x90_period_id=da.DimArray(axes=[range(150),per_len.lat,per_len.lon],dims=['ID','lat','lon'])
                TXx_in_x90=da.DimArray(axes=[year_uq,per_len.lat,per_len.lon],dims=['ID','lat','lon'])


                for lat in per_len.lat:
                    print lat
                    for lon in per_len.lon:
                        hw_id=np.where((seas[:,lat,lon]==1) & (state[:,lat,lon]==1) & (per_len[:,lat,lon]>=qu_90[scenario,lat,lon]) & np.isfinite(per_len[:,lat,lon]))[0].squeeze()
                        if len(hw_id)>1:
                            hw_years=year[per_mid[hw_id,lat,lon]-tas.time[0]]
                            for yr in set(hw_years):
                                TX_hw=[]
                                #plt.close()
                                #plt.plot(range(len(tas[:,lat,lon].values[year==yr])),tas[:,lat,lon].values[year==yr])
                                #plt.scatter(range(len(tas[:,lat,lon].values[year==yr])),state_check[:,lat,lon].values[year==yr])
                                for period_id,i in zip(hw_id[hw_years==yr],range(len(hw_id[hw_years==yr]))):
                                    days=np.arange(per_mid[period_id,lat,lon]-int(abs(per_len[period_id,lat,lon])/2.),per_mid[period_id,lat,lon]+int(round(abs(per_len[period_id,lat,lon])/2.)))
                                    tmp=tas[days,lat,lon].values
                                    x90_hottest_day[i,lat,lon]=np.max(tmp)
                                    TX_hw.append(x90_hottest_day[i,lat,lon])
                                    x90_cum_temp[i,lat,lon]=np.sum(tmp)
                                    x90_mean_temp[i,lat,lon]=np.sum(tmp)/float(abs(per_len[period_id,lat,lon]))
                                    x90_period_id[i,lat,lon]=period_id
                                    #plt.plot(day_in_year[np.array(days-tas.time[0],dtype='int')],tmp)

                                Txx=np.nanmax(tas[:,lat,lon].values[year==yr])
                                if Txx in TX_hw:
                                    TXx_in_x90[yr,lat,lon]=1
                                else:
                                    TXx_in_x90[yr,lat,lon]=0

                                print lat,Txx,TXx_in_x90[yr,lat,lon]
                                #plt.savefig('test.png')



                ds=da.Dataset({'x90_hottest_day':x90_hottest_day,'x90_cum_temp':x90_cum_temp,'x90_period_id':x90_period_id,'TXx_in_x90':TXx_in_x90,'x90_mean_temp':x90_mean_temp})
                ds.write_nc(out_file, mode='w')

                claim_run.close()
                os.system('rm '+claim_run_file)
