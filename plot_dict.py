import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import matplotlib.pylab as plt 

from scipy.optimize import curve_fit

from lmfit import  Model

os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
try:
    import plot_map as plot_map; reload(plot_map)
except ImportError:
    raise ImportError(
        "cannot find plot_map code")
from plot_map import col_conv
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')


seasons=['MAM','JJA','SON','DJF','year']

dataset='MIROC'
#dataset='NORESM1'

fit_dict={}
for scenario in ['All-Hist','Plus15-Future','Plus20-Future']:
	pkl_file = open('data/'+dataset+'_'+scenario+'_fits.pkl', 'rb')
	fit_dict[scenario] = pickle.load(pkl_file)	;	pkl_file.close()  

lat=fit_dict[scenario]['lat']
lon=fit_dict[scenario]['lon']

print lon,len(lon)
print lat,len(lat)


lat_plt=np.arange(-90,90,180/float(len(lat)))
lat_plt+=np.diff(lat_plt,1)[0]/2.
lon_plt=np.arange(0,360,360/float(len(lon)))
lon_plt+=np.diff(lon_plt,1)[0]/2.


os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
try:
    import plot_map as plot_map; reload(plot_map)
except ImportError:
    raise ImportError(
        "cannot find plot_map code")
from plot_map import col_conv
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')


# ---------------------- BIC difference -------------------------------------------
scenario='All-Hist'
plt.clf()
fig,axes=plt.subplots(nrows=5,ncols=2,figsize=(10,10))
axes=axes.flatten()
count=0
for season in ['MAM','JJA','SON','DJF']:
	for state,state_name in zip([-1,1],['cold','warm']):
		to_plot=np.zeros([len(lat),len(lon)])*np.nan
		for iy in range(len(lat)):
			for ix in range(len(lon)):
				try:
					tmp=fit_dict[scenario][season][state][str(lat[iy])+'_'+str(lon[ix])]
					to_plot[iy,ix]=tmp['double_exp']['bic']-tmp['single_exp']['bic']
				except Exception,e:
					pass

					
		im1=plot_map.plot_map(to_plot,lat_plt,lon_plt,color_palette=plt.cm.PiYG_r,color_range=[-20,20],limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3,contour=True,levels=[-100,-10,10,100],colors=['red','yellow','green'])
		axes[count].annotate('  '+dataset+'\n  '+season+' '+state_name, xy=(0, 0), xycoords='axes fraction', fontsize=14,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
		count+=1


axes[count].axis('off')
axes[count+1].axis('off')

m1, = axes[count+1].plot([], [], c='red' , marker='s',linestyle='none', markersize=20,label='double-exp preferred (BIC difference < -10)')
m2, = axes[count+1].plot([], [], c='yellow' , marker='s',linestyle='none', markersize=20,label='similar performance (-10 < BIC difference < 10)')
m4, = axes[count+1].plot([], [], c='green' , marker='s',linestyle='none', markersize=20,label='single-exp preferred (BIC difference > 10)')
axes[count+1].legend(loc='right',numpoints=1)

fig.tight_layout()
plt.savefig('plots/'+dataset+'_BIC_diff_'+scenario+'.png',dpi=300)


# ---------------------- b1 single-exp -------------------------------------------
scenario='All-Hist'
plt.clf()
fig,axes=plt.subplots(nrows=5,ncols=2,figsize=(10,10))
axes=axes.flatten()
count=0
for season in ['MAM','JJA','SON','DJF']:
	for state,state_name in zip([-1,1],['cold','warm']):
		to_plot_1=np.zeros([len(lat),len(lon)])*np.nan
		to_plot_2=np.zeros([len(lat),len(lon)])*np.nan
		to_plot_3=np.zeros([len(lat),len(lon)])*np.nan
		for iy in range(len(lat)):
			for ix in range(len(lon)):
				try:
					tmp=fit_dict[scenario][season][state][str(lat[iy])+'_'+str(lon[ix])]
					to_plot[iy,ix]=np.exp(-tmp['single_exp']['params']['b1'])*100
				except Exception,e:
					pass

		im1=plot_map.plot_map(to_plot,lat_plt,lon_plt,color_palette=plt.cm.plasma,color_range=[65,85],limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3)
		axes[count].annotate('  '+dataset+'\n  '+season+' '+state_name, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
		count+=1

axes[count].axis('off')
axes[count+1].axis('off')

cbar_ax=fig.add_axes([0,0.1,1,0.15])
cbar_ax.axis('off')
cb=fig.colorbar(im1,orientation='horizontal',label='$P$ $[\%]$',ax=cbar_ax)


fig.tight_layout()
plt.savefig('plots/'+dataset+'_single_exp_P_'+scenario+'.png',dpi=300)


# ---------------------- as Figure 5 -------------------------------------------
plt.clf()
fig,axes=plt.subplots(nrows=5,ncols=3,figsize=(10,7))
axes=axes.flatten()
count=0
for season in ['JJA','DJF']:
	for state,state_name in zip([-1,1],['cold','warm']):
		to_plot_1=np.zeros([len(lat),len(lon)])*np.nan
		to_plot_2=np.zeros([len(lat),len(lon)])*np.nan
		to_plot_3=np.zeros([len(lat),len(lon)])*np.nan
		for iy in range(len(lat)):
			for ix in range(len(lon)):
				try:
					tmp=fit_dict[scenario][season][state][str(lat[iy])+'_'+str(lon[ix])]
					to_plot_1[iy,ix]=np.exp(-tmp['double_exp']['params']['b2'])*100
					to_plot_2[iy,ix]=np.exp(-tmp['double_exp']['params']['b2'])*100-np.exp(-tmp['double_exp']['params']['b1'])*100
					to_plot_3[iy,ix]=tmp['double_exp']['params']['thr']
				except Exception,e:
					pass

		im1=plot_map.plot_map(to_plot_1,lat_plt,lon_plt,color_palette=plt.cm.plasma,color_range=[70,90],limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3)
		axes[count].annotate('  '+dataset+'\n  '+season+' '+state_name, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
		count+=1

		im2=plot_map.plot_map(to_plot_2,lat_plt,lon_plt,color_palette=plt.cm.PiYG,color_range=[-10,10],limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3)
		axes[count].annotate('  '+dataset+'\n  '+season+' '+state_name, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
		count+=1

		im3=plot_map.plot_map(to_plot_3,lat_plt,lon_plt,color_palette=plt.cm.summer,color_range=[4,14],limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3)
		axes[count].annotate('  '+dataset+'\n  '+season+' '+state_name, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
		count+=1

axes[count].axis('off')
axes[count+1].axis('off')
axes[count+2].axis('off')

cbar_ax=fig.add_axes([0.05,0.14,0.28,0.18])
cbar_ax.axis('off')
cb=fig.colorbar(im1,orientation='horizontal',label='$P_2$ $[\%]$',ax=cbar_ax)

cbar_ax=fig.add_axes([0.38,0.14,0.28,0.18])
cbar_ax.axis('off')
cb=fig.colorbar(im2,orientation='horizontal',label='$P_2 - P_1$ $[\%]$',ax=cbar_ax)

cbar_ax=fig.add_axes([0.71,0.14,0.28,0.18])
cbar_ax.axis('off')
cb=fig.colorbar(im3,orientation='horizontal',label='$d_{critical}$ in days',ax=cbar_ax)


#fig.suptitle(dataset)
fig.tight_layout()
plt.savefig('plots/'+dataset+'_double_exp_summary_'+scenario+'.png',dpi=300)













def plot_fit(tmp,out_file='plots/fit_example.png'):
	fig,ax= plt.subplots(nrows=1,ncols=1,figsize=(3,3))

	ax.plot(tmp['period_length'],tmp['count'])
	ax.plot(tmp['period_length'],tmp['single_exp']['best_fit'])
	ax.plot(tmp['period_length'],tmp['double_exp']['best_fit'])
	ax.set_yscale('log')

	plt.savefig(out_file)
	plt.clf()


tmp=fit_dict['All-Hist']['JJA'][1][str(lat[120])+'_'+str(lon[18])]
plot_fit(tmp,out_file='plots/fit_example.png')
















