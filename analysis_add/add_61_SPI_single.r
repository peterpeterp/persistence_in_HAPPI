library(ncdf4)
library(SPEI)

args = commandArgs(trailingOnly=TRUE)
print(paste('infile',args[1]))
print(paste('outfile',args[1]))


nc<-nc_open(args[1])
pr<-ncvar_get(nc,'pr')
time_index<-ncvar_get(nc,'time_index')

spi<-spi(ts(pr, freq=12, start=c(-13200,1)), 3, ref.start=c(-13200,1), ref.end=c(-1,12), na.rm = TRUE)$fitted

timedim <- ncdim_def(name="time",units="months since 1970-1-1 00:00:00",vals=time,unlim=FALSE)

spivar <- ncvar_def(name="SPI",units="-",dim=list(timedim),missval=-99999.9,longname=paste('SPI ',args[3],'months'))

print(spivar)
nc_out <- nc_create( args[2], spivar)
ncvar_put( nc_out, vals=spi)

nc_close(nc_out)
