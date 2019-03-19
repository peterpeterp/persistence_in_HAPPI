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

model = 'CAM4-2degree'
scenario = 'All-Hist'
var = 'pr'

os.system('mkdir -p raw_data/'+model+'/'+scenario+'/'+var)
os.chdir('raw_data/'+model+'/'+scenario+'/'+var)

for run in model_dict[model]['runs'][scenario]:
    print("downloading: pr_Aday_CAM4-2degree_All-Hist_est1_v1-0_"+run+"_20060101-20151231.nc")
    urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=ETH/CAM4-2degree/All-Hist/est1/v1-0/day/atmos/pr/"+run+"/pr_Aday_CAM4-2degree_All-Hist_est1_v1-0_"+run+"_20060101-20151231.nc","pr_Aday_CAM4-2degree_All-Hist_est1_v1-0_"+run+"_20060101-20151231.nc", hook)
    print('\n')

os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter')
scenario = 'Plus20-Future'
os.system('mkdir -p raw_data/'+model+'/'+scenario+'/'+var)
os.chdir('raw_data/'+model+'/'+scenario+'/'+var)


for run in model_dict[model]['runs'][scenario]:
    print("downloading: pr_Aday_CAM4-2degree_Plus20-Future_CMIP5-MMM-est1_v2-0_"+run+"_21060101-21151231.nc")
    urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=ETH/CAM4-2degree/Plus20-Future/CMIP5-MMM-est1/v2-0/day/atmos/pr/"+run+"/pr_Aday_CAM4-2degree_Plus20-Future_CMIP5-MMM-est1_v2-0_"+run+"_21060101-21151231.nc","pr_Aday_CAM4-2degree_Plus20-Future_CMIP5-MMM-est1_v2-0_"+run+"_21060101-21151231.nc", hook)
    print('\n')


os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter')
scenario = 'Plus15-Future'
os.system('mkdir -p raw_data/'+model+'/'+scenario+'/'+var)
os.chdir('raw_data/'+model+'/'+scenario+'/'+var)

for run in model_dict[model]['runs'][scenario]:
    print("downloading: pr_Aday_CAM4-2degree_Plus15-Future_CMIP5-MMM-est1_v2-0_"+run+"_21060101-21151231.nc")
    urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=ETH/CAM4-2degree/Plus15-Future/CMIP5-MMM-est1/v2-0/day/atmos/pr/"+run+"/pr_Aday_CAM4-2degree_Plus15-Future_CMIP5-MMM-est1_v2-0_"+run+"_21060101-21151231.nc","pr_Aday_CAM4-2degree_Plus15-Future_CMIP5-MMM-est1_v2-0_"+run+"_21060101-21151231.nc", hook)
    print('\n')
