import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Documents/Projects/weather_persistence/')
import persistence_support as persistence_support; reload(persistence_support)
from persistence_support import *

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

model_dict={'MIROC5':{'grid':'128x256','path':'/global/cscratch1/sd/pepflei/MIROC/MIROC5/'},
			'NorESM1':{'grid':'192x288','path':'/global/cscratch1/sd/pepflei/NCC/NorESM1-HAPPI/'},
			'ECHAM6-3-LR':{'grid':'96x192','path':'/global/cscratch1/sd/pepflei/MPI-M/ECHAM6-3-LR/'},
			'CAM4-2degree':{'grid':'96x144','path':'/global/cscratch1/sd/pepflei/ETH/CAM4-2degree/'},
}
