import sys
if (sys.version_info > (3, 0)):
  from urllib.request import urlretrieve
else:
  from urllib import urlretrieve
def hook(a,b,c): print(a*b,"/",c, "\r", end='')

import os,sys,glob,time,collections,signal,gc

os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter')

sys.path.append('persistence_in_HAPPI/')
import __settings
model_dict=__settings.model_dict

model = 'NorESM1'
scenario = 'All-Hist'
var = 'tas'

os.system('mkdir -P raw_data/'+model+'/'+sceanrio+'/'+var)
os.chdir('raw_data/'+model+'/'+sceanrio+'/'+var)

for run in model_dict[model]['runs'][scenario]:
    filename = "tas_Aday_NorESM1-HAPPI_All-Hist_est1_v1-0_run121_20060101-20160630.nc"
    print("downloading: "+filename)
    urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=NCC/NorESM1-HAPPI/All-Hist/est1/v1-0/day/atmos/tas/"+run+"/tas_Aday_NorESM1-HAPPI_All-Hist_est1_v1-0_"+run+"_20060101-20160630.nc",filename, hook)
    print('\n')
