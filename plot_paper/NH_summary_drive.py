import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,num2date
import cPickle as pickle
import dimarray as da
from scipy.optimize import curve_fit
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy import stats

import matplotlib.pylab as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import seaborn as sns
sns.set_style("whitegrid")
import matplotlib.ticker as mticker

sys.path.append('/Users/peterpfleiderer/Projects/allgemeine_scripte')
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

NH_regs={'ALA':{'color':'darkgreen','pos_off':(+10,+7),'summer':'JJA','winter':'DJF'},
		'WNA':{'color':'darkblue','pos_off':(+20,+15),'summer':'JJA','winter':'DJF'},
		'CNA':{'color':'gray','pos_off':(+8,-4),'summer':'JJA','winter':'DJF'},
		'ENA':{'color':'darkgreen','pos_off':(+18,-5),'summer':'JJA','winter':'DJF'},
		'CGI':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},
		# 'CAM':{'color':'darkcyan','pos_off':(+0,-5),'summer':'JJA','winter':'DJF'},

		'NEU':{'color':'darkgreen','pos_off':(-13,+0),'summer':'JJA','winter':'DJF'},
		'CEU':{'color':'darkblue','pos_off':(+9,+5),'summer':'JJA','winter':'DJF'},
		'CAS':{'color':'darkgreen','pos_off':(-8,+14),'summer':'JJA','winter':'DJF'},
		'NAS':{'color':'gray','summer':'JJA','winter':'DJF'},
		'TIB':{'color':'darkcyan','pos_off':(+2,-4),'summer':'JJA','winter':'DJF'},
		'EAS':{'color':'darkgreen','summer':'JJA','winter':'DJF'},

		'MED':{'color':'gray','pos_off':(-15,-5),'summer':'JJA','winter':'DJF'},
		'WAS':{'color':'darkcyan','pos_off':(-5,-1),'summer':'JJA','winter':'DJF'},
		'mid-lat':{'edge':'darkgreen','color':'none','alpha':1,'pos':(-142,42),'xlabel':'Period length [days]','ylabel':'Exceedence probability [%]','title':'','summer':'JJA','winter':'DJF','scaling_factor':1.3}}

all_regs=NH_regs.copy()

polygons=srex.copy()
polygons['mid-lat']={'points':[(-180,35),(180,35),(180,60),(-180,60)]}

icon_dict = {'storm_track':get_sample_data('/Users/peterpfleiderer/Projects/Persistence/plots/icons/weather.png')}

# ---------------------------- changes
def legend_plot(subax,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	subax.axis('off')

def axis_settings(subax,label=False,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	# subax.axis('off')
	return(subax)

def imscatter(x, y, image, ax=None, zoom=1):
    if ax is None:
        ax = plt.gca()
    try:
        image = plt.imread(image)
    except TypeError:
        # Likely already an array...
        pass
    im = OffsetImage(image, zoom=zoom)
    x, y = np.atleast_1d(x, y)
    artists = []
    for x0, y0 in zip(x, y):
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    ax.update_datalim(np.column_stack([x, y]))
    ax.autoscale()
    return artists

def distrs(subax,region,arg1=None,arg2=None,arg3=None,arg4=None,arg5=None):
	print('________'+region+'________')
	if region == 'CGI':
		for state,details in arg1[region].items():
			print(icon_dict[details['icon']])
			imscatter(details['x'], details['y'], icon_dict[details['icon']], zoom=0.05, ax=subax)

plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

legend_dict = {'warm':'warm','dry':'dry','dry-warm':'dry-warm','5mm':'rain'}

arg1 = {'ALA':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'WNA':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'CNA':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'ENA':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'CGI':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		# 'CAM':{'warm':{'x':1,'y':1,'icon':'storm_track'}},

		'NEU':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'CEU':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'CAS':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'NAS':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'TIB':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'EAS':{'warm':{'x':1,'y':1,'icon':'storm_track'}},

		'MED':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'WAS':{'warm':{'x':1,'y':1,'icon':'storm_track'}},
		'mid-lat':{'warm':{'x':1,'y':1,'icon':'storm_track'}}
}


fig,ax_map=srex_overview.srex_overview(distrs, axis_settings, polygons=polygons, reg_info=all_regs, x_ext=[-180,180], y_ext=[0,85], small_plot_size=0.08, legend_plot=legend_plot, legend_pos=[164,9], \
	arg1=arg1,
	title=None)
plt.savefig('plots/NH_summary_drive.png',dpi=600)
