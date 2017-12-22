def percentile_from_counts(y,count,qu):
	if qu>1:
		qu/=100.
	cum=np.cumsum(count)/float(np.sum(count))
	x1=y[cum<qu][-1]
	return x1+(qu-cum[cum<qu][-1])/(cum[cum>qu][0]-cum[cum<qu][-1])

tmp=big_dict[model][region][scenario]['JJA']['warm']
cum=np.cumsum(tmp['count'])/float(np.sum(tmp['count']))
per=tmp['period_length']

qu=0.75
npperc=np.percentile(persJJAw[model][scenario][region],qu*100)
ppperc=percentile_from_counts(tmp['period_length'],tmp['count'],qu*100)
plt.close()
plt.plot(per,cum)
plt.plot([per[cum>qu][0],per[cum>qu][0]],[0,1])
plt.plot([per[cum>qu][0]-1,per[cum>qu][0]-1],[0,1])
plt.plot([npperc,npperc],[0,1])
plt.plot([ppperc,ppperc],[0,1])
plt.plot([0,74],[qu,qu])
plt.savefig('plots/test.png')
print ppperc,npperc
