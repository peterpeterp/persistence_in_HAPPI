import os,sys,glob,time,collections,gc,pickle,textwrap
import numpy as np
from netCDF4 import Dataset,num2date
import dimarray as da
from statsmodels.sandbox.stats import multicomp
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection

import matplotlib
import cartopy.crs as ccrs
import cartopy
import seaborn as sns
import shapely
sns.set()
sns.set_style("whitegrid")
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [sns.color_palette("colorblind")[0],'white',sns.color_palette("colorblind")[4]])

sys.path.append('/p/projects/ikiimp/HAPPI/HAPPI_Peter/persistence_in_HAPPI/')
os.chdir('/p/projects/ikiimp/HAPPI/HAPPI_Peter/')

working_path='/p/tmp/pepflei/HAPPI/raw_data/reg_cor/'

state_dict = {
	'warm':'tas',
	'dry':'pr',
	'5mm':'pr',
	'dry-warm':'cpd',
	}

all_files = glob.glob('reg_cor/CAM4-2degree/cor_EKE*All-Hist*_warm*')
tmp = {}
for file_name in all_files:
	region = file_name.split('_')[-2]
	if region != 'NHml':
		tmp[region] = da.stack(da.read_nc(file_name),axis='statistic',align=True)
tmp = da.stack(tmp, align=True, axis='region')

merged = tmp['CEU'].copy() * np.nan
merged.values = np.nanmean(tmp,axis=0)




#
