library(ncdf4)
library(SPEI)


args = commandArgs(trailingOnly=TRUE)
print(paste('infile',args[1]))
print(paste('precip var name',args[2]))
print(paste('months',args[3]))
print(paste('first year',args[4]))
print(paste('calib. start year',args[5]))
print(paste('calib. end year',args[6]))
print(paste('outfile',args[7]))


nc<-nc_open(args[1])
pr<-ncvar_get(nc,args[2])

lon<-ncvar_get(nc,'lon')
lat<-ncvar_get(nc,'lat')
time<-ncvar_get(nc,'time')
'''
this is weird

spi=pr*NA
for (x in 1:length(lon)){
	cat(paste("--",x,proc.time()[3][[1]]))
	for (y in 1:length(lat)){
		spi[x,y,]<-spi(ts(pr[x,y,], freq=12, start=c(as.numeric(args[4]),1)), as.numeric(args[3]), ref.start=c(as.numeric(args[5]),1), ref.end=c(as.numeric(args[6]),12), na.rm = TRUE)$fitted
	}



	londim <- ncdim_def(name="lon",units="deg east",vals=lon)
	latdim <- ncdim_def(name="lat",units="deg north",vals=lat)
	# adapt time stamp
	timedim <- ncdim_def(name="time",units="days since 1860-1-1 00:00:00",vals=time,unlim=FALSE)

	spivar <- ncvar_def(name="SPI",units="-",dim=list(londim,latdim,timedim),missval=-99999.9,longname=paste('SPI ',args[3],'months'))

	nc_out <- nc_create( args[7], spivar )
	ncvar_put( nc_out, vals=spi)

	nc_close(nc_out)

}
'''
