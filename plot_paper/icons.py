import os,sys,glob,time,collections,gc,pickle,textwrap

for home_path in ['/Users/peterpfleiderer/Projects/Persistence','Dokumente/klima_uni/Persistence_small']:
	try:
		os.chdir(home_path)
	except:
		pass

os.chdir('persistence_in_HAPPI/plot_paper')
import __plot_imports; reload(__plot_imports); from __plot_imports import *
os.chdir('../../')

import os,sys,glob,time,collections,gc,pickle,textwrap

for home_path in ['/Users/peterpfleiderer/Projects/Persistence','Dokumente/klima_uni/Persistence_small']:
	try:
		os.chdir(home_path)
	except:
		pass

os.chdir('persistence_in_HAPPI/plot_paper')
from __plot_imports import *
os.chdir('../../')

fig,ax = plt.subplots(nrows=1, figsize=(7,7))
ax.axis('off')
ax.plot([-0.6,0.6],[-1,1] ,'r-', lw=50)
ax.plot([-1,1],[0.6,-0.6] ,'r-', lw=50)
ax.set_ylim(-1.3,1.3)
ax.set_xlim(-1.3,1.3)
plt.savefig('plots/icons/avoided.png', transparent=True)

fig,ax = plt.subplots(nrows=1, figsize=(7,7))
ax.axis('off')
ax.plot([-0.6,0.6],[-1,1] ,'r', linestyle=(0, (1, 1)), lw=50)
ax.plot([-1,1],[0.6,-0.6] ,'r', linestyle=(0, (1, 1)), lw=50)
ax.set_ylim(-1.3,1.3)
ax.set_xlim(-1.3,1.3)
plt.savefig('plots/icons/mitigated.png', transparent=True)

# fig,ax = plt.subplots(nrows=1, figsize=(7,7))
# ax.axis('off')
# ax.plot([-0.5,0.5],[-1,1] ,'r:', lw=50)
# ax.plot([-0.25,0.5],[-0.5,1] ,'r:', lw=50)
# ax.plot([-1,1],[0.5,-0.5] ,'r:', lw=50)
# ax.plot([-0.5,1],[0.25,-0.5] ,'r:', lw=50)
# ax.set_ylim(-1.3,1.3)
# ax.set_xlim(-1.3,1.3)
# plt.savefig('plots/icons/mitigated.png', transparent=True)
#


#
