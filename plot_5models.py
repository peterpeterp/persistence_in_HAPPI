import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
from statsmodels.sandbox.stats import multicomp


os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
import plot_map as plot_map; reload(plot_map)
from plot_map import col_conv
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')

sum_dict={}

tmp_1=da.read_nc('data/MIROC5_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_2=da.read_nc('data/MIROC5_SummaryKS.nc')['SummaryKS']
tmp_3=da.read_nc('data/MIROC5_SummaryFit.nc')['SummaryFit']
sum_dict['MIROC5']=da.concatenate((tmp_1,tmp_2,tmp_3),axis='type')

tmp_1=da.read_nc('data/NORESM1_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_2=da.read_nc('data/NORESM1_SummaryKS.nc')['SummaryKS']
tmp_3=da.read_nc('data/NORESM1_SummaryFit.nc')['SummaryFit']
sum_dict['NORESM1']=da.concatenate((tmp_1,tmp_2,tmp_3),axis='type')

tmp_1=da.read_nc('data/ECHAM6-3-LR_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_2=da.read_nc('data/ECHAM6-3-LR_SummaryKS.nc')['SummaryKS']
sum_dict['ECHAM6-3-LR']=da.concatenate((tmp_1,tmp_2),axis='type')

tmp_1=da.read_nc('data/CAM4-2degree_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_2=da.read_nc('data/CAM4-2degree_SummaryKS.nc')['SummaryKS']
sum_dict['CAM4-2degree']=da.concatenate((tmp_1,tmp_2),axis='type')


tmp_1=da.read_nc('../HadGHCND_persistence/data/HadGHCND_SummaryMeanQu.nc')['SummaryMeanQu']
tmp_3=da.read_nc('../HadGHCND_persistence/data/HadGHCND_SummaryFit.nc')['SummaryFit']
sum_dict['HadGHCND']=da.concatenate((tmp_1,tmp_3),axis='type')



# _________________________ clim mean
for season,state in zip(['JJA','DJF'],['warm','cold']):
	plt.clf()
	fig,axes=plt.subplots(nrows=6,ncols=1,figsize=(5,6))
	axes=axes.flatten()
	count=0

	for dataset in ['HadGHCND','MIROC5','NORESM1','CAM4-2degree','ECHAM6-3-LR']:
		tmp=sum_dict[dataset]
		to_plot=np.asarray(tmp['All-Hist'][season][state]['mean'])

		im1=plot_map.plot_map(to_plot,lat=tmp.lat,lon=tmp.lon,color_palette=plt.cm.jet,color_range=[3,7],limits=[-180,180,20,80],ax=axes[count],show=False,color_bar=False,marker_size=1)
		axes[count].annotate(dataset, xy=(0, 0), xycoords='axes fraction', fontsize=9,xytext=(0.5, 0.5), textcoords='offset points',ha='left', va='bottom', fontweight='bold')
		count+=1

	axes[count].axis('off')

	cbar_ax=fig.add_axes([0,0.15,1,0.15])
	cbar_ax.axis('off')
	cb=fig.colorbar(im1,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)

	plt.suptitle(season+' '+state+' persistence', fontweight='bold')
	#fig.tight_layout()
	plt.savefig('plots/'+season+'_'+state+'_mean_.png',dpi=300)

# _________________________ clim extreme
for season,state in zip(['JJA','DJF'],['warm','cold']):
	plt.clf()
	fig,axes=plt.subplots(nrows=6,ncols=1,figsize=(5,6))
	axes=axes.flatten()
	count=0

	for dataset in ['HadGHCND','MIROC5','NORESM1','CAM4-2degree','ECHAM6-3-LR']:
		tmp=sum_dict[dataset]
		to_plot=np.asarray(tmp['All-Hist'][season][state]['qu_95'])

		im1=plot_map.plot_map(to_plot,lat=tmp.lat,lon=tmp.lon,color_palette=plt.cm.jet,color_range=[7,21],limits=[-180,180,20,80],ax=axes[count],show=False,color_bar=False,marker_size=1)
		axes[count].annotate(dataset, xy=(0, 0), xycoords='axes fraction', fontsize=9,xytext=(0.5, 0.5), textcoords='offset points',ha='left', va='bottom', fontweight='bold')
		count+=1

	axes[count].axis('off')

	cbar_ax=fig.add_axes([0,0.1,1,0.15])
	cbar_ax.axis('off')
	cb=fig.colorbar(im1,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)

	plt.suptitle(season+' '+state+' persistence', fontweight='bold')
	#fig.tight_layout()
	plt.savefig('plots/'+season+'_'+state+'_qu_95_.png',dpi=300)






os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
import plot_map as plot_map; reload(plot_map)
from plot_map import col_conv
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')


# _________________________ diff mean
for season,state in zip(['JJA','DJF'],['warm','cold']):

	plt.clf()
	fig,axes=plt.subplots(nrows=5,ncols=1,figsize=(5,5))
	axes=axes.flatten()
	count=0

	color_range=[-0.5,0.5]

	for dataset in ['MIROC5','NORESM1','CAM4-2degree','ECHAM6-3-LR']:
	#for dataset in ['MIROC5','ECHAM6-3-LR']:
		tmp=sum_dict[dataset]
		to_plot=np.asarray(tmp['Plus20-Future'][season][state]['mean']-tmp['All-Hist'][season][state]['mean'])
		significance=np.asarray(tmp['Plus20-Future'][season][state]['KS_vs_All-Hist'])
		#significance=multicomp.multipletests(significance.reshape((len(tmp.lat)*len(tmp.lon))), method='fdr_bh')[1].reshape((len(tmp.lat),len(tmp.lon)))
		significance[significance>0.05]=0
		significance[np.isfinite(significance)==False]=0

		im1=plot_map.plot_map(to_plot,lat=tmp.lat,lon=tmp.lon,significance=significance,color_palette=plt.cm.PiYG_r,color_range=color_range,limits=[-180,180,20,80],ax=axes[count],show=False,color_bar=False)
		axes[count].annotate(dataset, xy=(0, 0), xycoords='axes fraction', fontsize=9,xytext=(0.5, 0.5), textcoords='offset points',ha='left', va='bottom', fontweight='bold')
		count+=1

	axes[count].axis('off')

	cbar_ax=fig.add_axes([0,0.2,1,0.15])
	cbar_ax.axis('off')
	cb=fig.colorbar(im1,orientation='horizontal',label='mean persistence [days]',ax=cbar_ax)
	cb.set_ticks(np.linspace(color_range[0], color_range[1], num=5, endpoint=True))
	cb.set_ticklabels(np.linspace(color_range[0], color_range[1], num=5, endpoint=True))

	plt.suptitle(season+' '+state+' persistence', fontweight='bold')
	#fig.tight_layout()
	plt.savefig('plots/'+season+'_'+state+'_mean_change.png',dpi=300)



# _________________________ diff 95th
for season,state in zip(['JJA','DJF'],['warm','cold']):

	plt.clf()
	fig,axes=plt.subplots(nrows=5,ncols=1,figsize=(5,5))
	axes=axes.flatten()
	count=0

	color_range=[-1.,1.]

	for dataset in ['MIROC5','NORESM1','CAM4-2degree','ECHAM6-3-LR']:
		tmp=sum_dict[dataset]
		to_plot=np.asarray(tmp['Plus20-Future'][season][state]['qu_95']-tmp['All-Hist'][season][state]['qu_95'])
		significance=np.asarray(tmp['Plus20-Future'][season][state]['KS_vs_All-Hist'])
		#significance=multicomp.multipletests(significance.reshape((len(tmp.lat)*len(tmp.lon))), method='fdr_bh')[1].reshape((len(tmp.lat),len(tmp.lon)))
		significance[significance>0.05]=0
		significance[np.isfinite(significance)==False]=0

		im1=plot_map.plot_map(to_plot,lat=tmp.lat,lon=tmp.lon,significance=significance,color_palette=plt.cm.PiYG_r,color_range=[-1,1],limits=[-180,180,20,80],ax=axes[count],show=False,color_bar=False,marker_size=1)
		axes[count].annotate(dataset, xy=(0, 0), xycoords='axes fraction', fontsize=9,xytext=(0.5, 0.5), textcoords='offset points',ha='left', va='bottom', fontweight='bold')
		count+=1

	axes[count].axis('off')

	cbar_ax=fig.add_axes([0,0.2,1,0.15])
	cbar_ax.axis('off')
	cb=fig.colorbar(im1,orientation='horizontal',label='95th percentile of persistence [days]',ax=cbar_ax)
	cb.set_ticks(np.linspace(color_range[0], color_range[1], num=5, endpoint=True))
	cb.set_ticklabels(np.linspace(color_range[0], color_range[1], num=5, endpoint=True))

	plt.suptitle(season+' '+state+' persistence', fontweight='bold')
	#fig.tight_layout()
	plt.savefig('plots/'+season+'_'+state+'_qu95_change.png',dpi=300)
