 nohup python $1 $2 $3  >out/$2+_+$3 & expect "nohup: ignoring input and redirecting stderr to stdout" { send "\r" }
