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

model = 'ECHAM6-3-LR'
scenario = 'All-Hist'
var = 'tas'

os.system('mkdir -p raw_data/'+model+'/'+scenario+'/'+var)
os.chdir('raw_data/'+model+'/'+scenario+'/'+var)

for run in model_dict[model]['runs'][scenario]:
    print("downloading: tas_Aday_ECHAM6-3-LR_All-Hist_est1_v1-0_"+run+"_20060101-20151231.nc")
    urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MPI-M/ECHAM6-3-LR/All-Hist/est1/v1-0/day/atmos/tas/"+run+"/tas_Aday_ECHAM6-3-LR_All-Hist_est1_v1-0_"+run+"_20060101-20151231.nc","tas_Aday_ECHAM6-3-LR_All-Hist_est1_v1-0_"+run+"_20060101-20151231.nc", hook)
    print('\n')
