library(ncdf4)
library(SPEI)

args = commandArgs(trailingOnly=TRUE)
print(paste('infile',args[1]))
print(paste('outfile',args[2]))

pr <- as.numeric(read.csv(args[1],sep=';',dec='.',header=FALSE))

spi<-spi(ts(pr, freq=12, start=c(-13200,1)), 3, ref.start=c(-13200,1), ref.end=c(-1,12), na.rm = TRUE)$fitted

write.table(matrix(as.character(spi),nrow=1), args[2], sep=";",row.names=FALSE, col.names=FALSE)
