from __future__ import print_function
import sys

if (sys.version_info > (3, 0)):
  from urllib.request import urlretrieve
else:
  from urllib import urlretrieve
def hook(a,b,c): print(a*b,"/",c, "\r", end="")

import os,sys,glob,time,collections,signal,gc

os.chdir('/p/tmp/pepflei/HAPPI/')

sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
import __settings
model_dict=__settings.model_dict

model = 'MIROC5'
scenario = 'All-Hist'
var = 'tas'

print('hey')

os.system('mkdir -p raw_data/'+model+'/'+scenario+'/'+var+'/tmp')
os.chdir('raw_data/'+model+'/'+scenario+'/'+var)

for run in ['run'+str(i).zfill(3) for i in range(111,161)]:
    if os.path.isfile("tas_Aday_MIROC5_All-Hist_CMIP5-MMM-est1_v2-0_"+run+"_20060101-20161231.nc") == False:

        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20060101-20061231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20060101-20061231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20060101-20061231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20070101-20071231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20070101-20071231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20070101-20071231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20080101-20081231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20080101-20081231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20080101-20081231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20090101-20091231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20090101-20091231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20090101-20091231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20100101-20101231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20100101-20101231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20100101-20101231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20110101-20111231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20110101-20111231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20110101-20111231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20120101-20121231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20120101-20121231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20120101-20121231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20130101-20131231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20130101-20131231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20130101-20131231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20140101-20141231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20140101-20141231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20140101-20141231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20150101-20151231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20150101-20151231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20150101-20151231.nc", hook)
        print('\n')
        print("downloading: tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20160101-20161231.nc")
        urlretrieve("http://portal.nersc.gov/cascade/data/rtrack.php?source=NERSCDisk&filename=MIROC/MIROC5/All-Hist/est1/v2-0/day/atmos/tas/"+run+"/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20160101-20161231.nc","tmp/tas_Aday_MIROC5_All-Hist_est1_v2-0_"+run+"_20160101-20161231.nc", hook)
        print('\n')

        os.system("cdo mergetime tmp/* tas_Aday_MIROC5_All-Hist_CMIP5-MMM-est1_v2-0_"+run+"_20060101-20161231.nc")
        os.system("rm tmp/*")
