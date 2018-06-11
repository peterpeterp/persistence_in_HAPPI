import os,sys,glob
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
from scipy import stats

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from statsmodels.regression.quantile_regression import QuantReg

def time_stamp(x):
        if x>0:
                year=int(x)
                day=round((x-int(x))*365)

                if day in range(0,32): month=1
                if day in range(32,60): month=2
                if day in range(60,91): month=3
                if day in range(91,121): month=4
                if day in range(121,152): month=5
                if day in range(152,182): month=6
                if day in range(182,213): month=7
                if day in range(213,244): month=8
                if day in range(244,274): month=9
                if day in range(274,305): month=10
                if day in range(305,336): month=11
                if day in range(336,366): month=12

                return year,month
        else: return None,None

variable='eke850'
seasons=['MAM','JJA','SON','DJF','4seasons']
quantiles=[0.05,0.25,0.5,0.75,0.95]

# to cor
in_file='data/eke/eke850_1979-2014_calendar_96x73_ID.nc'
nc_tocor=Dataset(in_file,'r')

toCor=nc_tocor.variables[variable][:,:]
ID_=nc_tocor.variables['ID'][:]   ;   nID=len(ID_)

lat_=nc_tocor.variables['lat'][:]
lon_=nc_tocor.variables['lon'][:]

year=nc_tocor.variables['year'][:]   ;   nt=len(year)
month=nc_tocor.variables['month'][:]


correlation=np.zeros([nID,5,2,5])*np.nan
correlation_qu=np.zeros([nID,5,2,5,3])*np.nan

for season,sea_ID in zip(seasons,range(5)):
        for state in [0,1]:


                # duration
                in_file='data/_TMean/91_7/gridded/91_7_TMean_duration_'+season+'.nc'
                nc_dur=Dataset(in_file,'r')


                for q in ID_-1:
                #       print q
                # for q in [475]:
                        dur=np.ma.getdata(nc_dur.variables['dur'][:,state,q])
                        mask=np.ma.getmask(nc_dur.variables['dur'][:,state,q])
                        dur=dur[mask==False]

                        dur_mid=np.ma.getdata(nc_dur.variables['dur_mid'][:,state,q])
                        dur_mid=dur_mid[mask==False]

                        if len(np.where(np.isfinite(dur))[0])>20:

                                y=dur.copy()*np.nan
                                for t,i in zip(dur_mid,range(len(dur))):
                                        yr,mth=time_stamp(t)
                                        if yr is not None:
                                          if len(np.where((year==yr) & (month==mth))[0])==1:
                                                  y[i]=toCor[np.where((year==yr) & (month==mth))[0],q]

                          if len(np.where(np.isfinite(y))[0])>20:

                                  notna=np.where(np.isfinite(y) & np.isfinite(dur))
                                  y=y[notna]
                                  dur=dur[notna]
                                  dur_mid=dur_mid[notna]

                                  if True:
                                          slope, intercept, r_value, p_value, std_err = stats.linregress(dur_mid,dur)
                                          mn=np.mean(dur)
                                          dur=dur-(intercept+slope*dur_mid)+mn


                                          slope, intercept, r_value, p_value, std_err = stats.linregress(dur_mid,y)
                                          mn=np.mean(y)
                                          y=y-(intercept+slope*dur_mid)+mn


                                  pearson_cor,pearson_cor_sig=stats.pearsonr(dur,y)
                                  correlation[q,sea_ID,state,0]=pearson_cor
                                  correlation[q,sea_ID,state,1]=pearson_cor_sig

                                  slope, intercept, r_value, p_value, std_err = stats.linregress(y,dur)
                                  correlation[q,sea_ID,state,2]=slope
                                  correlation[q,sea_ID,state,3]=p_value
                                  correlation[q,sea_ID,state,4]=intercept





                                  # print slope, intercept, r_value, p_value, std_err
                                  # plt.plot(y,dur,'o')
                                  # plt.plot(y,intercept+slope*y,'r')


                                  df=pd.DataFrame(data={'dur':dur,'y':y})
                                  mod = smf.quantreg('dur ~ y', df)
                                  for qu,qui in zip(quantiles,range(5)):
                                          try:
                                                  res = mod.fit(q=qu)
                                                  slope,p_value,interc=res.params['y'],res.pvalues['y'],res.params['Intercept']
                                                  correlation_qu[q,sea_ID,state,qui,:]=[slope,p_value,interc]
                                                  # plt.plot(y,interc+slope*y,'b--')
                                          except:
                                                  pass


                                  # plt.show()
                                  # asdasd


out_file='data/_TMean/91_7/gridded/91_7_TMean_duration_'+variable+'_cor.nc'
os.system('rm '+out_file)
nc_out=Dataset(out_file,'w')
nc_out.createDimension('ID',len(ID_))
nc_out.createDimension('seasons',5)
nc_out.createDimension('states',2)
nc_out.createDimension('quantiles',5)
nc_out.createDimension('quantile_outs',3)
nc_out.createDimension('outs',5)

outVar = nc_out.createVariable('ID', 'i2', 'ID')    ;   outVar[:] = ID_
outVar = nc_out.createVariable('lat', 'f', 'ID')    ;   outVar[:] = lat_
outVar = nc_out.createVariable('lon', 'f', 'ID')    ;   outVar[:] = lon_

outVar = nc_out.createVariable('season', 'S1', 'seasons')    ;   outVar[:] = seasons
outVar = nc_out.createVariable('quantiles', 'i2', 'quantiles')    ;   outVar[:] = quantiles
outVar = nc_out.createVariable('quantile_outs', 'S1', 'quantile_outs')    ;   outVar[:] = ['slope','p_value','intercept']
outVar = nc_out.createVariable('outs', 'S1', 'outs')    ;   outVar[:] = ['pearson_cor','pearson_cor_sig','slope','p_value','intercept']

outVar = nc_out.createVariable('correlation', 'f', ('ID','seasons','states','outs',))    ;   outVar[:] = correlation[:,:,:,:]
outVar = nc_out.createVariable('correlation_qu', 'f', ('ID','seasons','states','quantiles','quantile_outs',))    ;   outVar[:] = correlation_qu[:,:,:,:,:]
