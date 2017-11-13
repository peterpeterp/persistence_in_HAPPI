import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt 
import dimarray as da
from statsmodels.sandbox.stats import multicomp


os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
try:
    import plot_map as plot_map; reload(plot_map)
except ImportError:
    raise ImportError(
        "cannot find plot_map code")
from plot_map import col_conv
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')

tmp_1=da.read_nc('data/MIROC_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_2=da.read_nc('data/MIROC_SummaryKS.nc')['SummaryKS']
tmp_3=da.read_nc('data/MIROC_SummaryFit.nc')['SummaryFit']
MIROC=da.concatenate((tmp_1,tmp_2,tmp_3),axis='type')

tmp_1=da.read_nc('data/NORESM1_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_2=da.read_nc('data/NORESM1_SummaryKS.nc')['SummaryKS']
tmp_3=da.read_nc('data/NORESM1_SummaryFit.nc')['SummaryFit']
NORESM1=da.concatenate((tmp_1,tmp_2,tmp_3),axis='type')

tmp_1=da.read_nc('../HadGHCND_persistence/data/HadGHCND_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_3=da.read_nc('../HadGHCND_persistence/data/HadGHCND_SummaryFit.nc')['SummaryFit']
HadGHCND=da.concatenate((tmp_1,tmp_3),axis='type')

# _________________________ clim mean
for state in ['cold','warm']:
	plt.clf()
	fig,axes=plt.subplots(nrows=5,ncols=3,figsize=(12,8))
	axes=axes.flatten()
	count=0

	for season in ['MAM','JJA','SON','DJF']:
		for dataset,dataset_name in zip([HadGHCND,MIROC,NORESM1],['HadGHCND','MIROC','NORESM1']):
			to_plot=np.asarray(dataset['All-Hist'][season][state]['mean'])
			im1=plot_map.plot_map(to_plot,lat=dataset.lat,lon=dataset.lon,color_palette=plt.cm.jet,color_range=[3,7],limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3)
			axes[count].annotate('  '+season+'\n  '+state, xy=(0, 0), xycoords='axes fraction', fontsize=14,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
			count+=1
			
	axes[0].set_title('HadGHCND')
	axes[1].set_title('MIROC')
	axes[2].set_title('NORESM1')

	axes[count].axis('off')
	axes[count+1].axis('off')
	axes[count+2].axis('off')

	cbar_ax=fig.add_axes([0,0.1,1,0.15])
	cbar_ax.axis('off')
	cb=fig.colorbar(im1,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)

	fig.tight_layout()
	plt.savefig('plots/'+state+'_climatology.png',dpi=300)

# _________________________ clim qu_95
for state in ['cold','warm']:
	plt.clf()
	fig,axes=plt.subplots(nrows=5,ncols=3,figsize=(12,8))
	axes=axes.flatten()
	count=0

	for season in ['MAM','JJA','SON','DJF']:
		for dataset,dataset_name in zip([HadGHCND,MIROC,NORESM1],['HadGHCND','MIROC','NORESM1']):
			to_plot=np.asarray(dataset['All-Hist'][season][state]['qu_95'])
			im1=plot_map.plot_map(to_plot,lat=dataset.lat,lon=dataset.lon,color_palette=plt.cm.jet,color_range=[6,22],limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3)
			axes[count].annotate('  '+season+'\n  '+state, xy=(0, 0), xycoords='axes fraction', fontsize=14,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
			count+=1
			
	axes[0].set_title('HadGHCND')
	axes[1].set_title('MIROC')
	axes[2].set_title('NORESM1')

	axes[count].axis('off')
	axes[count+1].axis('off')
	axes[count+2].axis('off')

	cbar_ax=fig.add_axes([0,0.1,1,0.15])
	cbar_ax.axis('off')
	cb=fig.colorbar(im1,orientation='horizontal',label='95th percentile persistence [days]',ax=cbar_ax)

	fig.tight_layout()
	plt.savefig('plots/'+state+'_climatology_qu95.png',dpi=300)


# _________________________ mean difference
for state in ['cold','warm']:
	plt.clf()
	fig,axes=plt.subplots(nrows=5,ncols=2,figsize=(8,8))
	axes=axes.flatten()
	count=0
	for season in ['MAM','JJA','SON','DJF']:
		for dataset,dataset_name in zip([MIROC,NORESM1],['MIROC','NORESM1']):
			to_plot=np.asarray(dataset['Plus20-Future'][season][state]['mean']-dataset['All-Hist'][season][state]['mean'])
			significance=np.asarray(dataset['Plus20-Future'][season][state]['KS_vs_All-Hist'])
			significance=multicomp.multipletests(significance.reshape((len(dataset.lat)*len(dataset.lon))), method='fdr_bh')[1].reshape((len(dataset.lat),len(dataset.lon)))
			significance[significance>0.05]=0
			significance[np.isfinite(significance)==False]=0

			im1=plot_map.plot_map(to_plot,lat=dataset.lat,lon=dataset.lon,significance=significance,color_palette=plt.cm.PiYG_r,color_range=[-0.2,0.2],limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.05)
			axes[count].annotate('  '+season+'\n  '+state, xy=(0, 0), xycoords='axes fraction', fontsize=14,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
			count+=1
			
	axes[0].set_title('MIROC')
	axes[1].set_title('NORESM1')

	axes[count].axis('off')
	axes[count+1].axis('off')

	cbar_ax=fig.add_axes([0,0.1,1,0.15])
	cbar_ax.axis('off')
	cb=fig.colorbar(im1,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)

	fig.tight_layout()
	plt.savefig('plots/'+state+'_meand_diff_20_vs_hist.png',dpi=600)




# _________________________ bic difference
for state in ['cold','warm']:
	plt.clf()
	fig,axes=plt.subplots(nrows=5,ncols=3,figsize=(12,8))
	axes=axes.flatten()
	count=0
	for season in ['MAM','JJA','SON','DJF']:
		for dataset,dataset_name in zip([HadGHCND,MIROC,NORESM1],['HadGHCND','MIROC','NORESM1']):
			to_plot=np.asarray(dataset['All-Hist'][season][state]['doub_BIC']-dataset['All-Hist'][season][state]['sing_BIC'])
			im1=plot_map.plot_map(to_plot,lat=dataset.lat,lon=dataset.lon,color_palette=plt.cm.plasma,color_range=[-10,10],limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3,contour=True,levels=[-100,-10,10,100],colors=['red','yellow','green'])
			axes[count].annotate('  '+season+'\n  '+state, xy=(0, 0), xycoords='axes fraction', fontsize=14,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
			count+=1
			
	axes[0].set_title('HadGHCND')
	axes[1].set_title('MIROC')
	axes[2].set_title('NORESM1')

	axes[count].axis('off')
	axes[count+1].axis('off')
	axes[count+2].axis('off')

	m1, = axes[count+1].plot([], [], c='red' , marker='s',linestyle='none', markersize=20,label='double-exp preferred (BIC difference < -10)')
	m2, = axes[count+1].plot([], [], c='yellow' , marker='s',linestyle='none', markersize=20,label='similar performance (-10 < BIC difference < 10)')
	m4, = axes[count+1].plot([], [], c='green' , marker='s',linestyle='none', markersize=20,label='single-exp preferred (BIC difference > 10)')
	axes[count+1].legend(loc='right',numpoints=1)

	fig.tight_layout()
	plt.savefig('plots/'+state+'_bic_diff.png',dpi=300)
















