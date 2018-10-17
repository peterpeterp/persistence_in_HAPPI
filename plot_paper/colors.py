import os,sys,glob,time,collections,gc

import matplotlib.pylab as plt

import seaborn as sns
sns.set_style("whitegrid")


sys.path.append('/Users/peterpfleiderer/Projects/allgemeine_scripte')
import srex_overview as srex_overview; reload(srex_overview)
os.chdir('/Users/peterpfleiderer/Projects/Persistence')

try:
	os.chdir('/Users/peterpfleiderer/Projects/Persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

# https://www.webucator.com/blog/2015/03/python-color-constants-module/

current_palette = sns.color_palette(['#FF3030','#FF8C00','#8B3A62','#1C86EE','#00FFFF','#458B74'])
sns.palplot(current_palette)
plt.savefig('plots/paper/colors.png',dpi=600)


current_palette = sns.cubehelix_palette(8, start=0.5, rot=-0.75)
sns.palplot(current_palette)
plt.savefig('plots/paper/colors.png',dpi=600)


#
