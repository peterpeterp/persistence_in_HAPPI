import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import cPickle as pickle
import matplotlib.pylab as plt 
import dimarray as da
from scipy.optimize import curve_fit
from lmfit import  Model
import pandas as pd


os.chdir('/Users/peterpfleiderer/Documents/Projects/Scripts/allgemeine_scripte')
try:
    import plot_map as plot_map; reload(plot_map)
    import srex_overview as srex_overview; reload(srex_overview)
except:
	print 'Plot Functions not found'
os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence')

try:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/HAPPI_persistence/')
except:
	os.chdir('/global/homes/p/pepflei/')

pkl_file = open('data/srex_dict.pkl', 'rb')
srex = pickle.load(pkl_file)	;	pkl_file.close()

seasons=['MAM','JJA','SON','DJF']
dataset='MIROC'
scenario='Plus20-Future'

def counter_to_pers(counter,state):
	pers_tmp=np.array(range(1,max([state*key+1 for key in counter.keys()])))
	count,pers=[],[]
	for pp,i in zip(pers_tmp,range(len(pers_tmp))):
		if pp*state in counter.keys(): 
			if abs(pp*state)!=0:
				count.append(counter[pp*state])
				pers.append(pp)
	count=np.array(count)
	pers=np.array(pers)
	return count,pers

def double_exp(x,a1,b1,b2,thr):
	x=np.array(x)
	y=x.copy()*np.nan
	y[x<=thr]	=	a1*np.exp(-b1*x[x<=thr])
	y[x>thr]	=	a1*np.exp((b2-b1)*thr)*np.exp(-b2*(x[x>thr]))
	return y 

def single_exp(x,a1,b1):
	x=np.array(x)
	return a1*np.exp(-b1*x)

def two_exp(x,a1,b1,a2,b2):
	x=np.array(x)
	y=x.copy()*np.nan
	y	=	a1*np.exp(-b1*x)+a2*np.exp(-b2*x)
	return y 

def all_fits(count,pers,plot=False,subax=None,do_two_expo=False):
	tmp={}

	# single
	try:
		popt, pcov = curve_fit(single_exp,pers[2::],count[2::])
		model=Model(single_exp)
		model.set_param_hint('a1', value=popt[0],vary=False)
		model.set_param_hint('b1', value=popt[1],vary=False)
		result = model.fit(count[2::], x=pers[2::])
		tmp['single_exp']={'bic':result.bic,'params':result.best_values,'best_fit':result.best_fit,'error':None}
	except Exception,e:
		tmp['single_exp']={'bic':None,'params':None,'best_fit':None,'error':str(e)}


	# double
	try:
		popt_, pcov = curve_fit(double_exp,pers[2::],count[2::],p0=[popt[0],popt[1],popt[1],7.],bounds=([0,0,0,5.],[np.inf,np.inf,np.inf,14.]))
		doubleM=Model(double_exp)
		doubleM.set_param_hint('a1', value=popt_[0],vary=False)
		doubleM.set_param_hint('b1', value=popt_[1],vary=False)
		doubleM.set_param_hint('b2', value=popt_[2],vary=False)
		doubleM.set_param_hint('thr', value=popt_[3],vary=False)
		result = doubleM.fit(count[2::], x=pers[2::])
		tmp['double_exp']={'bic':result.bic,'params':result.best_values,'best_fit':result.best_fit,'error':None}
	except Exception,e: 
		tmp['double_exp']={'bic':None,'params':None,'best_fit':None,'error':str(e)}

	if do_two_expo:
		try:
			popt_, pcov = curve_fit(two_exp,pers[2::],count[2::],p0=[popt[0]*0.1,popt[1],popt[0]*10,popt[1]],bounds=([0,0,0,0],[np.inf,np.inf,np.inf,np.inf]))
			doubleM=Model(two_exp)
			doubleM.set_param_hint('a1', value=popt_[0],vary=False)
			doubleM.set_param_hint('b1', value=popt_[1],vary=False)
			doubleM.set_param_hint('a2', value=popt_[2],vary=False)
			doubleM.set_param_hint('b2', value=popt_[3],vary=False)
			result = doubleM.fit(count[2::], x=pers[2::])
			tmp['two_exp']={'bic':result.bic,'params':result.best_values,'best_fit':result.best_fit,'error':None}
		except Exception,e: 
			tmp['two_exp']={'bic':None,'params':None,'best_fit':None,'error':str(e)}

	if plot:
		subax.plot(pers[2::],count[2::])
		subax.plot(pers[2::],tmp['single_exp']['best_fit'],label='single '+str(round(tmp['single_exp']['bic'],2)))
		subax.plot(pers[2::],tmp['double_exp']['best_fit'],label='double '+str(round(tmp['double_exp']['bic'],2)))
		subax.plot(pers[2::],tmp['two_exp']['best_fit'],label='two '+str(round(tmp['two_exp']['bic'],2)))
		subax.set_yscale('log')
		subax.set_xlim((0,40))
		subax.set_ylim((100,count[2]))
		if tmp['double_exp']['params']['b2']>tmp['double_exp']['params']['b1']:
			subax.plot([2,40],[1000,1000])
		subax.set_title(region)

	return tmp

# fig = plt.figure(figsize=(9,6))
# ax_big=fig.add_axes([0,0,1,1])
# all_fits(region_dict['NAS']['DJF']['cold']['count'],region_dict['NAS']['DJF']['cold']['pers'],plot=True,subax=ax_big)
# plt.savefig('plots/NAS.png')

if False:
	pkl_file = open('data/'+dataset+'_'+scenario+'_counter.pkl', 'rb')
	distr_dict = pickle.load(pkl_file)	;	pkl_file.close()  

	region_dict={}
	for region in srex.keys():	
		region_dict[region]={}
		tmp={}
		for season in seasons:
			region_dict[region][season]={'cold':{},'warm':{}}
			tmp[season]=collections.Counter()
		polygon=Polygon(srex[region]['points'])
		for x in distr_dict['lon']:
			if x>180:
				x__=x-360
			else:
				x__=x
			for y in distr_dict['lat']:
				if polygon.contains(Point(x__,y)):
					for season in seasons:
						if len(distr_dict[str(y)+'_'+str(x)][season].keys())>10:
							tmp[season]+=distr_dict[str(y)+'_'+str(x)][season]

		for season in seasons:
			for state,state_name in zip([-1,1],['cold','warm']):
				count,pers=counter_to_pers(tmp[season],-1)
				region_dict[region][season][state_name]['period_length']=pers
				region_dict[region][season][state_name]['count']=count


	output = open('data/'+dataset+'_'+scenario+'_regional_distrs.pkl', 'wb')
	pickle.dump(region_dict, output)
	output.close()

else: 
	pkl_file = open('data/'+dataset+'_'+scenario+'_regional_distrs.pkl', 'rb')
	region_dict = pickle.load(pkl_file)	;	pkl_file.close()

for region in srex.keys():
	for season in seasons:
		for state in ['cold','warm']:
			count=region_dict[region][season][state]['count']
			pers=region_dict[region][season][state]['pers']
			region_dict[region][season][state]=all_fits(count,pers,plot=False)



def example_plot(subax):
	subax.plot([1,1],[1,1],label='projections')
	subax.plot([1,1],[1,1],label='single-exp')
	subax.plot([1,1],[1,1],label='double-exp')
	subax.set_yscale('log')
	subax.set_xlim((0,40))
	subax.set_ylim((100,1000000))
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom='on') 
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft='on') 
	subax.set_title('example')
	subax.legend(loc='best',fontsize=12)

def test_plot(subax,region):
	tmp=region_dict[region]['DJF']['cold']
	count=tmp['count']
	pers=tmp['period_length']
	subax.plot(pers[2::],count[2::])
	subax.plot(pers[2::],tmp['single_exp']['best_fit'],label='single '+str(round(tmp['single_exp']['bic'],2)))
	subax.plot(pers[2::],tmp['double_exp']['best_fit'],label='double '+str(round(tmp['double_exp']['bic'],2)))
	#subax.plot(pers[2::],tmp['two_exp']['best_fit'],label='two '+str(round(tmp['two_exp']['bic'],2)))
	subax.set_yscale('log')
	subax.set_xlim((0,40))
	subax.set_ylim((100,1000000))
	subax.tick_params(axis='x',which='both',bottom='on',top='on',labelbottom='off') 
	subax.tick_params(axis='y',which='both',left='on',right='on',labelleft='off') 
	if tmp['double_exp']['params']['b2']>tmp['double_exp']['params']['b1']:
		subax.plot([2,40],[1000,1000])
	subax.annotate('   '+region, xy=(0, 0), xycoords='axes fraction', fontsize=10,xytext=(-5, 5), textcoords='offset points',ha='left', va='bottom')


srex_overview.srex_overview(test_plot,srex_polygons=srex,output_name='plots/test.png',example_plot=example_plot)





