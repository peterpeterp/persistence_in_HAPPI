import os,sys,glob,time,collections,gc,itertools
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import matplotlib.pylab as plt
import dimarray as da
from scipy.optimize import curve_fit
from lmfit import  Model
import pandas as pd

sys.path.append('/global/homes/p/pepflei/weather_persistence/')
sys.path.append('/Users/peterpfleiderer/Documents/Projects/weather_persistence/')
from persistence_functions import *


sys.path.append('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/persistence_in_models/')
from persistence import *


def test_persistence(N):
	ind=np.random.random(N)
	# ind[-5:]=-1
	ind[-2]=np.nan
	ind[ind<0.5]=-1
	ind[ind>=0.5]=1
	ind=np.array(ind,'i')
	print(ind[0:100])

	start_time = time.time()
	print(period_identifier(ind)[0:100])
	print("--- basic_and_understandable %s seconds ---" % (time.time() - start_time))

	start_time = time.time()
	print(period_identifier_cy(ind)[0:100])
	print("--- basic_and_understandable_cython %s seconds ---" % (time.time() - start_time))

	start_time = time.time()
	print(optimized_period_identifier(ind)[0:100])
	print("--- optimized_period_identifier %s seconds ---" % (time.time() - start_time))

test_persistence(10000000)
