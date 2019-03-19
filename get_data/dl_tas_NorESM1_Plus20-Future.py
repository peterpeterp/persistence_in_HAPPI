from __future__ import print_function
import sys

if (sys.version_info > (3, 0)):
  from urllib.request import urlretrieve
else:
  from urllib import urlretrieve
def hook(a,b,c): print(a*b,"/",c, "\r", end="")

import os,sys,glob,time,collections,signal,gc

os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter')

sys.path.append('persistence_in_HAPPI/')
import __settings
model_dict=__settings.model_dict

model = 'NorESM1'
scenario = 'Plus20-Future'
var = 'tas'

os.system('mkdir -p raw_data/'+model+'/'+scenario+'/'+var)
os.chdir('raw_data/'+model+'/'+scenario+'/'+var)

for run in model_dict[model]['runs'][scenario]:
    print("downloading: tas_Aday_NorESM1-HAPPI_Plus20-Future_CMIP5-MMM-est1_v2-0_"+run+"_21060101-21160630.nc")
    urlretrieve("nttps://portal.nersc.gov/c20c/data/NCC/NorESM1-HAPPI/Plus20-Future/CMIP5-MMM-est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_NorESM1-HAPPI_Plus20-Future_CMIP5-MMM-est1_v2-0_"+run+"_21060101-21160630.nc","tas_Aday_NorESM1-HAPPI_Plus20-Future_CMIP5-MMM-est1_v2-0_"+run+"_21060101-21160630.nc", hook)
    print('\n')
