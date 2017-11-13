import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt 
import dimarray as da

os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
try:
    import plot_map as plot_map; reload(plot_map)
except ImportError:
    raise ImportError(
        "cannot find plot_map code")
from plot_map import col_conv
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')

def slope_to_prob(x):
	return np.exp(-x)*100

def do_nothing(x):
	return x

def normal_map(dataset,dataset_name,scenario,variable,color_label=None,color_range=None,operation=do_nothing):
	plt.clf()
	fig,axes=plt.subplots(nrows=5,ncols=2,figsize=(10,10))
	axes=axes.flatten()
	count=0
	for season in ['MAM','JJA','SON','DJF']:
		for state in ['cold','warm']:
			to_plot=np.asarray(operation(dataset[scenario][season][state][variable]))
			im1=plot_map.plot_map(to_plot,lat=dataset.lat,lon=dataset.lon,color_palette=plt.cm.PiYG_r,color_range=color_range,limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3)
			axes[count].annotate('  '+dataset_name+'\n  '+season+' '+state, xy=(0, 0), xycoords='axes fraction', fontsize=14,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
			count+=1

	axes[count].axis('off')
	axes[count+1].axis('off')

	cbar_ax=fig.add_axes([0,0.1,1,0.15])
	cbar_ax.axis('off')
	if color_label is None: color_label=variable
	cb=fig.colorbar(im1,orientation='horizontal',label=color_label,ax=cbar_ax)

	fig.tight_layout()
	plt.savefig('plots/'+dataset_name+'_'+variable+'_'+scenario+'.png',dpi=300)

def diff_map(dataset,dataset_name,scenario_2,scenario_1,variable,signi_scenario=None,singi_variable=None,signi_level=0.05,color_label=None,color_range=None,operation=do_nothing):
	plt.clf()
	fig,axes=plt.subplots(nrows=5,ncols=2,figsize=(10,10))
	axes=axes.flatten()
	count=0
	for season in ['MAM','JJA','SON','DJF']:
		for state in ['cold','warm']:
			to_plot=np.asarray(operation(dataset[scenario_2][season][state][variable])-operation(dataset[scenario_1][season][state][variable]))
			if singi_variable is not None: 
				significance=np.asarray(dataset[signi_scenario][season][state][singi_variable])
				significance[significance>signi_level]=0
				significance[np.isfinite(significance)==False]=0
			else:
				significance=None
			im1=plot_map.plot_map(to_plot,lat=dataset.lat,lon=dataset.lon,significance=significance,color_palette=plt.cm.PiYG_r,color_range=color_range,limits=[-180,180,-65,80],ax=axes[count],show=False,color_bar=False,marker_size=0.3)
			axes[count].annotate('  '+dataset_name+'\n  '+season+' '+state, xy=(0, 0), xycoords='axes fraction', fontsize=14,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')
			count+=1

	axes[count].axis('off')
	axes[count+1].axis('off')

	cbar_ax=fig.add_axes([0,0.1,1,0.15])
	cbar_ax.axis('off')
	if color_label is None: color_label=variable
	cb=fig.colorbar(im1,orientation='horizontal',label=color_label,ax=cbar_ax)

	fig.tight_layout()
	plt.savefig('plots/'+dataset_name+'_diff_'+variable+'_'+scenario_2+'_vs_'+scenario_1+'.png',dpi=300)


tmp_1=da.read_nc('data/MIROC_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_2=da.read_nc('data/MIROC_SummaryKS.nc')['SummaryKS']
tmp_3=da.read_nc('data/MIROC_SummaryFit.nc')['SummaryFit']
MIROC=da.concatenate((tmp_1,tmp_2,tmp_3),axis='type')
lon,lat=MIROC.lon,MIROC.lat

tmp_1=da.read_nc('data/NORESM1_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_2=da.read_nc('data/NORESM1_SummaryKS.nc')['SummaryKS']
#tmp_3=da.read_nc('data/NORESM1_SummaryFit.nc')['SummaryFit']
NORESM1=da.concatenate((tmp_1,tmp_2),axis='type')
lon,lat=NORESM1.lon,NORESM1.lat


diff_map(dataset=MIROC,dataset_name='MIROC',
	scenario_2='Plus20-Future',scenario_1='All-Hist',variable='mean',
	signi_scenario='Plus20-Future',singi_variable='KS_vs_All-Hist',signi_level=0.05,
	color_label='mean persistence [days]',color_range=[-0.2,0.2])

diff_map(dataset=NORESM1,dataset_name='NORESM1',
	scenario_2='Plus20-Future',scenario_1='All-Hist',variable='mean',
	signi_scenario='Plus20-Future',singi_variable='KS_vs_All-Hist',signi_level=0.05,
	color_label='mean persistence [days]',color_range=[-0.2,0.2])


diff_map(dataset=MIROC,dataset_name='MIROC',
	scenario_2='Plus20-Future',scenario_1='All-Hist',variable='qu_95',
	signi_scenario='Plus20-Future',singi_variable='KS_vs_All-Hist',signi_level=0.05,
	color_label='95th percentile persistence [days]',color_range=[-2,2])

diff_map(dataset=NORESM1,dataset_name='NORESM1',
	scenario_2='Plus20-Future',scenario_1='All-Hist',variable='qu_95',
	signi_scenario='Plus20-Future',singi_variable='KS_vs_All-Hist',signi_level=0.05,
	color_label='95th percentile persistence [days]',color_range=[-2,2])

# diff_map('Plus20-Future','All-Hist','sing_b',color_label='P2 [%]',color_range=[-2,2],operation=slope_to_prob)
# normal_map('All-Hist','qu_95',color_label='95 quantile [days]',color_range=[8,20])

normal_map(MIROC,'MIROC','All-Hist','mean',color_label='mean [days]',color_range=[-7,7])






