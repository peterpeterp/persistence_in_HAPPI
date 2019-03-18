import sys
if (sys.version_info > (3, 0)):
  from urllib.request import urlretrieve
else:
  from urllib import urlretrieve
def hook(a,b,c): print(a*b,"/",c, "\r", end='')

import os,sys,glob,time,collections,signal,gc

os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter')
model=sys.argv[1]

sys.path.append('persistence_in_HAPPI/')
import __settings
model_dict=__settings.model_dict

for scenario in ['All-Hist','Plus20-Future','Plus15-Future']:
    for run in model_dict[model]['runs'][scenario]:
        filename = "tas_Aday_"+model+"_"+scenario+"_est1_v1-0_"+run+"_20060101-20160630.nc"
        print("downloading: ",filename)
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=NCC/NorESM1-HAPPI/"+scenario+"/est1/v1-0/day/atmos/tas/run121/tas_Aday_NorESM1-HAPPI_All-Hist_est1_v1-0_run121_20060101-20160630.nc","tas_Aday_NorESM1-HAPPI_All-Hist_est1_v1-0_run121_20060101-20160630.nc", hook)
        print('\n')
